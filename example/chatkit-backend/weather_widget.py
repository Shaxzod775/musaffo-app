"""
Weather forecast widget for ChatKit.
Displays current weather and forecast for a given location.
Modern design inspired by AccuWeather.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from chatkit.widgets import (
    Badge,
    Box,
    Card,
    Col,
    Icon,
    Row,
    Spacer,
    Text,
    Title,
)


def get_weather_emoji(weather_code: int, is_night: bool = False) -> str:
    """
    Get emoji icon for weather condition.

    Args:
        weather_code: WMO Weather interpretation code
        is_night: Whether it's nighttime

    Returns:
        Emoji representation of weather
    """
    # Night icons
    if is_night:
        if weather_code == 0 or weather_code == 1:
            return "🌙"  # Clear night
        elif weather_code == 2:
            return "☁️"  # Partly cloudy night

    # Day icons
    if weather_code == 0 or weather_code == 1:
        return "☀️"  # Clear/Sunny
    elif weather_code == 2:
        return "⛅"  # Partly cloudy
    elif weather_code == 3:
        return "☁️"  # Cloudy
    elif weather_code == 45 or weather_code == 48:
        return "🌫️"  # Foggy
    elif weather_code in [51, 53, 55, 56, 57]:
        return "🌧️"  # Drizzle
    elif weather_code in [61, 63, 65, 66, 67]:
        return "🌧️"  # Rain
    elif weather_code in [71, 73, 75, 77, 85, 86]:
        return "❄️"  # Snow
    elif weather_code in [80, 81, 82]:
        return "🌦️"  # Rain showers
    elif weather_code == 95 or weather_code == 96 or weather_code == 99:
        return "⛈️"  # Thunderstorm
    else:
        return "🌡️"  # Default


def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return (celsius * 9/5) + 32


def render_weather_widget(
    location: str,
    temperature: float,
    temp_min: float,
    temp_max: float,
    condition: str,
    humidity: int,
    wind_speed: float,
    weather_code: int = 0,
    forecast: list[dict[str, Any]] | None = None,
    hourly_forecast: list[dict[str, Any]] | None = None,
    current_time: datetime | None = None,
) -> Card:
    """
    Render a modern weather forecast widget.

    Args:
        location: City or location name
        temperature: Current temperature in Celsius
        temp_min: Today's minimum temperature in Celsius
        temp_max: Today's maximum temperature in Celsius
        condition: Weather condition description
        humidity: Humidity percentage
        wind_speed: Wind speed in km/h
        forecast: Optional list of daily forecast data (6 days)
        hourly_forecast: Optional list of hourly forecast data (24 hours)
        current_time: Current datetime
    """
    if current_time is None:
        current_time = datetime.now()

    # Convert temperatures
    temp_c = temperature
    temp_f = celsius_to_fahrenheit(temperature)
    temp_min_c = temp_min
    temp_max_c = temp_max
    temp_min_f = celsius_to_fahrenheit(temp_min)
    temp_max_f = celsius_to_fahrenheit(temp_max)

    # Determine if it's night (between 6 PM and 6 AM)
    is_night = current_time.hour >= 18 or current_time.hour < 6

    # Get weather emoji based on current weather code
    weather_emoji = get_weather_emoji(weather_code, is_night)

    # Format current time
    day_of_week = current_time.strftime("%A")  # Monday, Tuesday, etc.
    time_str = current_time.strftime("%I:%M %p")  # 9:57 PM

    # ==================== HEADER ====================
    # Modern gradient header with large temperature display
    header = Box(
        background={"light": "purple-600", "dark": "slate-800"},
        padding={"x": 4, "y": 4},
        children=[
            # Title and Location
            Row(
                align="center",
                gap=2,
                padding={"bottom": 2},
                children=[
                    Text(
                        value="Погода",
                        size="md",
                        weight="semibold",
                        color={"light": "white", "dark": "white"}
                    ),
                    Text(value="•", size="sm", color="alpha-60"),
                    Text(
                        value=location,
                        size="md",
                        color={"light": "purple-100", "dark": "slate-300"}
                    ),
                    Spacer(),
                    # Weather icon (moved to title row)
                    Text(
                        value=weather_emoji,
                        size="xl",
                    ),
                ],
            ),
            # Main temperature display
            Row(
                align="baseline",
                gap=1,
                children=[
                    Title(
                        value=f"{temp_c:.0f}",
                        size="2xl",
                        weight="bold",
                        color={"light": "white", "dark": "white"}
                    ),
                    Text(
                        value="°C",
                        size="xl",
                        color={"light": "white", "dark": "white"}
                    ),
                ],
            ),
            # Condition description
            Text(
                value=condition,
                size="md",
                color={"light": "purple-100", "dark": "slate-300"},
                padding={"top": 1}
            ),
        ],
    )

    # Location is now in the header, so we don't need a separate section

    # ==================== WEEKLY FORECAST ====================
    weekly_forecast_items = []
    if forecast and len(forecast) > 0:
        for day_data in forecast[:6]:  # Show max 6 days
            day_name = day_data.get("day", "")
            temp_min = day_data.get("temperature_min", 0)
            temp_max = day_data.get("temperature_max", 0)
            weather_code = day_data.get("weather_code", 0)
            emoji = get_weather_emoji(weather_code, False)

            weekly_forecast_items.append(
                Col(
                    align="center",
                    gap=1,
                    flex=1,
                    padding={"y": 2, "x": 1},
                    children=[
                        Text(value=day_name, size="sm", weight="medium", color="alpha-70"),
                        Text(value=emoji, size="lg"),
                        Text(value=f"{temp_max:.0f}°", size="sm", weight="medium"),
                        Text(value=f"{temp_min:.0f}°", size="xs", color="alpha-50"),
                    ],
                )
            )

    weekly_forecast = None
    if weekly_forecast_items:
        weekly_forecast = Box(
            padding={"x": 4, "y": 3},
            border={"top": {"size": 1, "color": "alpha-10"}},
            children=[
                Row(
                    gap=1,
                    children=weekly_forecast_items,
                ),
            ],
        )

    # ==================== HOURLY GRAPH ====================
    # Simplified hourly display (ChatKit doesn't support custom charts)
    hourly_section = None
    if hourly_forecast and len(hourly_forecast) > 0:
        hourly_items = []
        # Show every 3rd hour to fit better
        for i in range(0, min(24, len(hourly_forecast)), 3):
            hour_data = hourly_forecast[i]
            time_str = hour_data.get("time", "")
            temp = hour_data.get("temperature", 0)

            # Extract hour from ISO time string (e.g., "2024-11-24T18:00")
            try:
                hour_dt = datetime.fromisoformat(time_str)
                hour_label = hour_dt.strftime("%I %p")  # "06 PM"
            except:
                hour_label = time_str[-5:]  # Fallback

            hourly_items.append(
                Col(
                    align="center",
                    gap=1,
                    flex=1,
                    children=[
                        Text(value=f"{temp:.0f}°", size="xs", weight="medium"),
                        Text(value="•", size="sm", color="alpha-40"),
                        Text(value=hour_label, size="xs", color="alpha-50"),
                    ],
                )
            )

        if hourly_items:
            # Temperature graph visualization using dots
            graph_row = Row(
                gap=0,
                children=hourly_items,
            )

            hourly_section = Box(
                padding={"x": 4, "top": 3, "bottom": 2},
                border={"top": {"size": 1, "color": "alpha-10"}},
                children=[
                    Text(
                        value="Hourly Forecast",
                        size="xs",
                        weight="medium",
                        color="alpha-60",
                        padding={"bottom": 2}
                    ),
                    graph_row,
                ],
            )

    # ==================== ADDITIONAL DETAILS ====================
    # Display feels like, humidity, and wind in a compact grid
    details = Box(
        padding={"x": 4, "y": 3},
        border={"top": {"size": 1, "color": "alpha-10"}},
        children=[
            # First row: Feels like and Humidity
            Row(
                gap=6,
                padding={"bottom": 2},
                children=[
                    # Feels like
                    Row(
                        flex=1,
                        gap=2,
                        align="center",
                        children=[
                            Text(value="Ощущается как:", size="sm", color="alpha-70"),
                            Text(
                                value=f"{temp_c:.0f}°C",
                                size="sm",
                                weight="semibold"
                            ),
                        ],
                    ),
                    # Humidity
                    Row(
                        flex=1,
                        gap=2,
                        align="center",
                        children=[
                            Text(value="Влажность:", size="sm", color="alpha-70"),
                            Text(
                                value=f"{humidity}%",
                                size="sm",
                                weight="semibold"
                            ),
                        ],
                    ),
                ],
            ),
            # Second row: Wind speed
            Row(
                gap=2,
                align="center",
                children=[
                    Text(value="Скорость ветра:", size="sm", color="alpha-70"),
                    Text(
                        value=f"{wind_speed:.0f} м/с",
                        size="sm",
                        weight="semibold"
                    ),
                ],
            ),
        ],
    )

    # ==================== BUILD WIDGET ====================
    # Simplified structure without footer and location section
    children = [header]

    # Add details section with feels like, humidity, and wind
    children.append(details)

    # Optionally add weekly forecast if available
    if weekly_forecast:
        children.append(weekly_forecast)

    # Optionally add hourly forecast if available
    if hourly_section:
        children.append(hourly_section)

    return Card(
        key="weather-forecast",
        size="md",
        padding=0,
        children=children,
    )


def weather_widget_copy_text(
    location: str,
    temperature: float,
    condition: str,
) -> str:
    """Generate copy text for the weather widget."""
    return f"Weather in {location}: {temperature:.1f}°C, {condition}"
