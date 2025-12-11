"""
FastAPI Backend for Air Quality Eco Fund
Using OpenAI Agents SDK with WebSearchTool for intelligent responses
"""

import os
import json
import asyncio
import re
import logging
from typing import AsyncIterator, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response, JSONResponse
from dotenv import load_dotenv
import httpx

# OpenAI Agents SDK imports
from agents import Agent, Runner, WebSearchTool, RunConfig, ModelSettings, function_tool

# ChatKit imports
from chatkit.store import Store, NotFoundError
from chatkit.server import ChatKitServer, StreamingResult
from chatkit.types import (
    ThreadMetadata,
    ThreadItem,
    ThreadStreamEvent,
    UserMessageItem,
    AssistantMessageItem,
    AssistantMessageContent,
    ThreadItemDoneEvent,
    Page,
    Attachment,
)
from chatkit.server import stream_widget

# Import custom widgets
from weather_widget import render_weather_widget
from aqi_widget import render_aqi_widget, get_aqi_category, detect_language

# Load environment variables
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Air Quality Eco Fund API",
    description="Backend API with IQAir integration and ChatKit support",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
IQAIR_API_KEY = os.getenv("IQAIR_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set OpenAI API key for agents SDK
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY or ""


# ============= WebSearchTool Setup =============

web_search_tool = WebSearchTool(
    search_context_size="medium",
    user_location={
        "type": "approximate",
        "city": "Tashkent",
        "country": "UZ",
        "region": "Tashkent"
    }
)


# ============= Agent Setup =============

# System instructions for the agent
AGENT_INSTRUCTIONS = """Ты - интеллектуальный ассистент для приложения Musaffo.
Твоя цель - помогать пользователям с информацией о качестве воздуха и экологических инициативах.

Инструкции по тону:
- Будь заботливым и ориентированным на действия.
- Используй простой язык, избегай сложных терминов.
- Отвечай на языке пользователя (русский, узбекский, английский).

ВАЖНО - Использование инструментов:

1. **get_weather_widget** - Показывает интерактивный виджет погоды. Используй когда:
   - Пользователь спрашивает про погоду, температуру, прогноз
   - Пользователь хочет узнать "какая сегодня погода", "сколько градусов", "будет ли дождь"
   - Любые вопросы связанные с метеоусловиями

2. **get_aqi_widget** - Показывает интерактивный виджет качества воздуха (AQI). Используй когда:
   - Пользователь спрашивает про качество воздуха, AQI, загрязнение
   - Пользователь хочет узнать "можно ли гулять", "нужна ли маска", "какой воздух сегодня"
   - Вопросы про смог, PM2.5, экологию воздуха
   - Пользователь беспокоится о здоровье из-за воздуха

3. **web_search** - Для поиска актуальных новостей и информации в интернете.

КРИТИЧНО: После использования ЛЮБОГО инструмента, ты ОБЯЗАН дать финальный текстовый ответ пользователю. НИКОГДА не заканчивай без текстового ответа.

MARKDOWN ФОРМАТИРОВАНИЕ:
- Используй правильное markdown форматирование с переносами строк
- Для нумерованных списков: каждый пункт на НОВОЙ СТРОКЕ
- Используй **жирный** для выделения, заголовки ## где уместно

Примеры ответов на частые вопросы:

1. Вопрос: Что делает ваш проект?
Ответ:
Наш проект помогает вам защитить здоровье от смога и реально влиять на чистоту воздуха в городе.
Musaffo показывает, когда воздух опасен, и помогает купить средства защиты (маски, фильтры). С каждой покупки часть денег идет в Эко-Фонд на посадку деревьев.

2. Вопрос: Для кого предназначен этот продукт?
Ответ:
Для каждого жителя Ташкента, кто хочет защитить своё здоровье и здоровье близких от загрязнённого воздуха."""


# ============= Agent Tools for Widgets =============

# Global variable to store widget data for streaming
_pending_widget = None


@function_tool
async def get_weather_widget(city: str = "Tashkent") -> str:
    """
    Показывает интерактивный виджет с текущей погодой и прогнозом.
    Используй этот инструмент когда пользователь спрашивает о погоде, температуре, прогнозе.

    Args:
        city: Название города (по умолчанию Ташкент)

    Returns:
        Краткое описание погоды для включения в ответ
    """
    global _pending_widget

    logger.info(f"get_weather_widget called for city: {city}")
    weather_data = await fetch_weather_data(city)

    if weather_data:
        # Store widget data for later rendering
        _pending_widget = {
            "type": "weather",
            "data": weather_data
        }

        return f"Погода в {weather_data['location']}: {weather_data['temperature']:.0f}°C, {weather_data['condition']}. Влажность: {weather_data['humidity']}%, Ветер: {weather_data['wind_speed']:.0f} м/с."
    else:
        return f"Не удалось получить данные о погоде для {city}. Попробуйте позже."


@function_tool
async def get_aqi_widget(city: str = "Tashkent") -> str:
    """
    Показывает интерактивный виджет с данными о качестве воздуха (AQI).
    Используй этот инструмент когда пользователь спрашивает о качестве воздуха, загрязнении, AQI, смоге.

    Args:
        city: Название города (по умолчанию Ташкент)

    Returns:
        Краткое описание качества воздуха для включения в ответ
    """
    global _pending_widget

    logger.info(f"get_aqi_widget called for city: {city}")
    aqi_data = await fetch_aqi_data(city)

    if aqi_data:
        # Store widget data for later rendering
        _pending_widget = {
            "type": "aqi",
            "data": aqi_data
        }

        # Add health recommendation based on AQI
        recommendation = ""
        if aqi_data["aqi"] <= 50:
            recommendation = "Воздух чистый, можно свободно гулять!"
        elif aqi_data["aqi"] <= 100:
            recommendation = "Качество воздуха приемлемое."
        elif aqi_data["aqi"] <= 150:
            recommendation = "Чувствительным людям лучше ограничить время на улице."
        elif aqi_data["aqi"] <= 200:
            recommendation = "Рекомендуется носить маску на улице."
        else:
            recommendation = "Воздух опасен! Оставайтесь дома, используйте очиститель воздуха."

        return f"Качество воздуха в {aqi_data['city']}: AQI {aqi_data['aqi']} ({aqi_data['category']}). Основной загрязнитель: {aqi_data['pollutant']}. {recommendation}"
    else:
        return f"Не удалось получить данные о качестве воздуха для {city}. Попробуйте позже."


# Create the agent with tools
agent_tools = [web_search_tool, get_weather_widget, get_aqi_widget]

musaffo_agent = Agent(
    name="Musaffo Assistant",
    model="gpt-5-mini",
    instructions=AGENT_INSTRUCTIONS,
    tools=agent_tools,
)


# ============= Weather & AQI Data Fetchers =============

async def fetch_weather_data(location: str = "Tashkent") -> dict | None:
    """Fetch weather data from Open-Meteo API."""
    try:
        async with httpx.AsyncClient() as client:
            # Get coordinates
            geo_response = await client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": location, "count": 1, "language": "ru", "format": "json"},
                timeout=10.0
            )

            if geo_response.status_code != 200:
                return None

            geo_data = geo_response.json()
            if not geo_data.get("results"):
                return None

            result = geo_data["results"][0]
            lat = result["latitude"]
            lon = result["longitude"]
            location_name = result["name"]
            country = result.get("country", "")

            # Get weather data
            weather_response = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
                    "hourly": "temperature_2m,weather_code",
                    "daily": "weather_code,temperature_2m_max,temperature_2m_min",
                    "timezone": "auto",
                    "forecast_days": 7
                },
                timeout=10.0
            )

            if weather_response.status_code != 200:
                return None

            weather_data = weather_response.json()
            current = weather_data["current"]
            daily = weather_data.get("daily", {})
            hourly = weather_data.get("hourly", {})

            weather_codes = {
                0: "Ясно", 1: "Преимущественно ясно", 2: "Переменная облачность", 3: "Облачно",
                45: "Туман", 48: "Туман", 51: "Легкая морось",
                61: "Легкий дождь", 63: "Умеренный дождь", 65: "Сильный дождь",
                71: "Легкий снег", 73: "Умеренный снег", 75: "Сильный снег",
                80: "Ливень", 95: "Гроза"
            }

            # Build forecast
            forecast = []
            if daily and "time" in daily:
                for i in range(min(7, len(daily["time"]))):
                    date_str = daily["time"][i]
                    date_obj = datetime.fromisoformat(date_str)
                    day_name = date_obj.strftime("%a")

                    forecast.append({
                        "day": day_name,
                        "temperature_min": daily["temperature_2m_min"][i],
                        "temperature_max": daily["temperature_2m_max"][i],
                        "weather_code": daily["weather_code"][i]
                    })

            # Build hourly forecast
            hourly_forecast = []
            if hourly and "time" in hourly:
                for i in range(min(24, len(hourly["time"]))):
                    hourly_forecast.append({
                        "time": hourly["time"][i],
                        "temperature": hourly["temperature_2m"][i]
                    })

            return {
                "location": f"{location_name}, {country}" if country else location_name,
                "temperature": current["temperature_2m"],
                "temp_min": daily["temperature_2m_min"][0] if daily.get("temperature_2m_min") else current["temperature_2m"],
                "temp_max": daily["temperature_2m_max"][0] if daily.get("temperature_2m_max") else current["temperature_2m"],
                "condition": weather_codes.get(current["weather_code"], "Неизвестно"),
                "humidity": current["relative_humidity_2m"],
                "wind_speed": current["wind_speed_10m"],
                "weather_code": current["weather_code"],
                "forecast": forecast,
                "hourly_forecast": hourly_forecast
            }
    except Exception as e:
        logger.error(f"Weather fetch error: {e}")
        return None


async def fetch_aqi_data(city: str = "Tashkent") -> dict | None:
    """Fetch AQI data from IQAir API."""
    if not IQAIR_API_KEY:
        return None

    try:
        async with httpx.AsyncClient() as client:
            # Get coordinates
            geo_response = await client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": city, "count": 1, "language": "ru", "format": "json"},
                timeout=10.0
            )

            if geo_response.status_code != 200:
                return None

            geo_data = geo_response.json()
            if not geo_data.get("results"):
                return None

            result = geo_data["results"][0]
            lat = result["latitude"]
            lon = result["longitude"]

            # Get AQI from IQAir
            iqair_response = await client.get(
                "https://api.airvisual.com/v2/nearest_city",
                params={
                    "lat": lat,
                    "lon": lon,
                    "key": IQAIR_API_KEY
                },
                timeout=15.0
            )

            if iqair_response.status_code != 200:
                return None

            iqair_data = iqair_response.json()
            if iqair_data.get("status") != "success":
                return None

            data = iqair_data.get("data", {})
            current = data.get("current", {})
            pollution = current.get("pollution", {})
            weather = current.get("weather", {})

            aqi_value = int(pollution.get("aqius", 0))
            category, _ = get_aqi_category(aqi_value)

            pollutant_map = {
                "p2": "PM2.5", "p1": "PM10", "o3": "O3",
                "n2": "NO2", "s2": "SO2", "co": "CO"
            }
            main_pollutant = pollution.get("mainus", "p2")

            return {
                "city": data.get("city", city),
                "aqi": aqi_value,
                "category": category,
                "scale": "US AQI",
                "pollutant": pollutant_map.get(main_pollutant, "PM2.5"),
                "temp": f"{round(weather.get('tp', 0))}°C",
                "humidity": f"{round(weather.get('hu', 0))}%",
                "wind": f"{round(weather.get('ws', 0) * 3.6)} км/ч",
                "updated": datetime.now().strftime("%H:%M, %d %B")
            }
    except Exception as e:
        logger.error(f"AQI fetch error: {e}")
        return None


# ============= In-Memory Store Implementation =============

@dataclass
class _ThreadState:
    thread: ThreadMetadata
    items: List[ThreadItem]


class MemoryStore(Store[dict[str, Any]]):
    """Simple in-memory store for ChatKit"""

    def __init__(self) -> None:
        self._threads: Dict[str, _ThreadState] = {}
        self._item_counter = 0

    def generate_item_id(self, prefix: str, thread: ThreadMetadata, context: dict) -> str:
        self._item_counter += 1
        return f"{prefix}_{self._item_counter}"

    async def load_thread(self, thread_id: str, context: dict[str, Any]) -> ThreadMetadata:
        state = self._threads.get(thread_id)
        if not state:
            raise NotFoundError(f"Thread {thread_id} not found")
        return state.thread

    async def save_thread(self, thread: ThreadMetadata, context: dict[str, Any]) -> None:
        state = self._threads.get(thread.id)
        if state:
            state.thread = thread
        else:
            self._threads[thread.id] = _ThreadState(thread=thread, items=[])

    async def load_threads(
        self, limit: int, after: str | None, order: str, context: dict[str, Any]
    ) -> Page[ThreadMetadata]:
        threads = list(state.thread for state in self._threads.values())
        return Page(data=threads[:limit], has_more=len(threads) > limit, after=None)

    async def delete_thread(self, thread_id: str, context: dict[str, Any]) -> None:
        self._threads.pop(thread_id, None)

    async def load_thread_items(
        self, thread_id: str, after: str | None, limit: int, order: str, context: dict[str, Any]
    ) -> Page[ThreadItem]:
        state = self._threads.get(thread_id)
        items = state.items if state else []
        return Page(data=items[:limit], has_more=len(items) > limit, after=None)

    async def add_thread_item(
        self, thread_id: str, item: ThreadItem, context: dict[str, Any]
    ) -> None:
        if thread_id not in self._threads:
            self._threads[thread_id] = _ThreadState(
                thread=ThreadMetadata(id=thread_id, created_at=datetime.utcnow()),
                items=[]
            )
        self._threads[thread_id].items.append(item)

    async def save_item(self, thread_id: str, item: ThreadItem, context: dict[str, Any]) -> None:
        await self.add_thread_item(thread_id, item, context)

    async def load_item(self, thread_id: str, item_id: str, context: dict[str, Any]) -> ThreadItem:
        state = self._threads.get(thread_id)
        if state:
            for item in state.items:
                if item.id == item_id:
                    return item
        raise NotFoundError(f"Item {item_id} not found")

    async def delete_thread_item(self, thread_id: str, item_id: str, context: dict[str, Any]) -> None:
        state = self._threads.get(thread_id)
        if state:
            state.items = [i for i in state.items if i.id != item_id]

    async def save_attachment(self, attachment: Attachment, context: dict[str, Any]) -> None:
        pass

    async def load_attachment(self, attachment_id: str, context: dict[str, Any]) -> Attachment:
        raise NotFoundError("Attachments not supported")

    async def delete_attachment(self, attachment_id: str, context: dict[str, Any]) -> None:
        pass


# ============= ChatKit Server Implementation =============

class MusaffoChatKitServer(ChatKitServer[dict[str, Any]]):
    """Custom ChatKit server for Musaffo Air Quality app using OpenAI Agents SDK"""

    def __init__(self):
        self.store = MemoryStore()
        super().__init__(self.store)

    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        """Generate AI response using OpenAI Agents SDK with WebSearchTool and ChatKit Widgets"""
        global _pending_widget

        # Get user message content
        user_text = ""
        if input_user_message and input_user_message.content:
            for content_item in input_user_message.content:
                if hasattr(content_item, 'text'):
                    user_text = content_item.text
                    break

        if not user_text:
            user_text = "Привет"

        try:
            logger.info(f"Running agent with input: {user_text[:100]}...")

            # Reset pending widget before running agent
            _pending_widget = None

            # Run the agent - it will decide whether to use weather/AQI tools
            result = await Runner.run(
                musaffo_agent,
                user_text,
                run_config=RunConfig(
                    model_settings=ModelSettings(
                        max_tokens=2048,
                    ),
                ),
                max_turns=10,
            )

            # Check if agent triggered a widget
            if _pending_widget:
                widget_info = _pending_widget
                _pending_widget = None  # Reset

                if widget_info["type"] == "weather":
                    weather_data = widget_info["data"]
                    widget = render_weather_widget(
                        location=weather_data["location"],
                        temperature=weather_data["temperature"],
                        temp_min=weather_data["temp_min"],
                        temp_max=weather_data["temp_max"],
                        condition=weather_data["condition"],
                        humidity=weather_data["humidity"],
                        wind_speed=weather_data["wind_speed"],
                        weather_code=weather_data["weather_code"],
                        forecast=weather_data.get("forecast"),
                        hourly_forecast=weather_data.get("hourly_forecast"),
                    )
                    # Stream widget using official ChatKit stream_widget
                    async for event in stream_widget(
                        thread,
                        widget,
                        generate_id=lambda item_type: self.store.generate_item_id(item_type, thread, context),
                    ):
                        yield event

                elif widget_info["type"] == "aqi":
                    aqi_data = widget_info["data"]
                    # Detect language from user's request
                    lang = detect_language(user_text)
                    widget = render_aqi_widget(
                        city=aqi_data["city"],
                        aqi=aqi_data["aqi"],
                        category=None,  # Will be auto-detected based on language
                        scale=aqi_data["scale"],
                        pollutant=aqi_data["pollutant"],
                        temp=aqi_data["temp"],
                        humidity=aqi_data["humidity"],
                        wind=aqi_data["wind"],
                        updated=aqi_data["updated"],
                        lang=lang,
                    )
                    # Stream widget using official ChatKit stream_widget
                    async for event in stream_widget(
                        thread,
                        widget,
                        generate_id=lambda item_type: self.store.generate_item_id(item_type, thread, context),
                    ):
                        yield event

            # Get final output from agent
            full_response = result.final_output or "Не удалось получить ответ"

            logger.info(f"Agent response: {full_response[:100]}...")

            # Send final message
            message_id = self.store.generate_item_id("msg", thread, context)
            yield ThreadItemDoneEvent(
                item=AssistantMessageItem(
                    thread_id=thread.id,
                    id=message_id,
                    created_at=datetime.utcnow(),
                    content=[AssistantMessageContent(text=full_response)],
                )
            )

        except Exception as e:
            logger.error(f"Agent error: {e}", exc_info=True)
            message_id = self.store.generate_item_id("msg", thread, context)
            yield ThreadItemDoneEvent(
                item=AssistantMessageItem(
                    thread_id=thread.id,
                    id=message_id,
                    created_at=datetime.utcnow(),
                    content=[AssistantMessageContent(text=f"Ошибка: {str(e)}")],
                )
            )


# Initialize ChatKit server
chatkit_server = MusaffoChatKitServer()


# ============= API Endpoints =============

@app.get("/")
async def root():
    return {"status": "ok", "message": "Musaffo API", "version": "1.0.0"}


@app.get("/api/air-quality")
async def api_get_air_quality(city: str = "Tashkent", country: str = "Uzbekistan"):
    """Direct API endpoint for air quality data"""
    if not IQAIR_API_KEY:
        return {"error": "IQAir API key not configured"}

    async with httpx.AsyncClient() as client:
        try:
            url = "https://api.airvisual.com/v2/city"
            params = {
                "city": city,
                "state": "Toshkent Shahri" if city == "Tashkent" else city,
                "country": country,
                "key": IQAIR_API_KEY
            }
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            return {"status": "success", "data": data.get("data", {})}
        except Exception as e:
            return {"status": "error", "error": str(e)}


@app.post("/api/chatkit")
async def chatkit_endpoint(request: Request) -> Response:
    """ChatKit endpoint using OpenAI Agents SDK"""
    try:
        payload = await request.body()
        result = await chatkit_server.process(payload, {"request": request})

        if isinstance(result, StreamingResult):
            return StreamingResponse(result, media_type="text/event-stream")
        if hasattr(result, "json"):
            return Response(content=result.json, media_type="application/json")
        return JSONResponse(result)
    except Exception as e:
        logger.error(f"ChatKit error: {e}", exc_info=True)
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/upload-url")
async def get_upload_url(request: Request):
    return {"upload_url": "", "file_url": ""}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
