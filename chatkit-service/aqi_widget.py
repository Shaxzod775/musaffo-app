"""
AQI (Air Quality Index) widget for ChatKit.
Displays air quality information for Tashkent.
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


# Translations for widget labels
TRANSLATIONS = {
    "ru": {
        "title": "Качество воздуха",
        "updated": "Обновлено",
        "temp": "Темп.",
        "humidity": "Влажн.",
        "wind": "Ветер",
        "good": "Хорошо",
        "moderate": "Умеренно",
        "unhealthy_sensitive": "Вредно для чувствительных",
        "unhealthy": "Вредно",
        "very_unhealthy": "Очень вредно",
        "hazardous": "Опасно",
    },
    "uz": {
        "title": "Havo sifati",
        "updated": "Yangilangan",
        "temp": "Harorat",
        "humidity": "Namlik",
        "wind": "Shamol",
        "good": "Yaxshi",
        "moderate": "O'rtacha",
        "unhealthy_sensitive": "Sezgirlar uchun zararli",
        "unhealthy": "Zararli",
        "very_unhealthy": "Juda zararli",
        "hazardous": "Xavfli",
    },
    "en": {
        "title": "Air Quality",
        "updated": "Updated",
        "temp": "Temp",
        "humidity": "Humidity",
        "wind": "Wind",
        "good": "Good",
        "moderate": "Moderate",
        "unhealthy_sensitive": "Unhealthy for Sensitive",
        "unhealthy": "Unhealthy",
        "very_unhealthy": "Very Unhealthy",
        "hazardous": "Hazardous",
    },
}


def detect_language(text: str) -> str:
    """Detect language from text based on character patterns."""
    text_lower = text.lower()

    # Check for Cyrillic characters (Russian)
    cyrillic_chars = sum(1 for c in text if '\u0400' <= c <= '\u04FF')

    # Check for Uzbek-specific Latin patterns
    uz_patterns = ["o'", "g'", "sh", "ch", "ng", "qanday", "qancha", "havo", "sifat", "ko'rsat"]
    has_uz_pattern = any(p in text_lower for p in uz_patterns)

    if cyrillic_chars > len(text) * 0.3:
        return "ru"
    elif has_uz_pattern:
        return "uz"
    else:
        return "en"


def get_aqi_category(aqi: int, lang: str = "ru") -> tuple[str, str]:
    """
    Get AQI category and color based on value.

    Args:
        aqi: Air Quality Index value
        lang: Language code (ru, uz, en)

    Returns:
        Tuple of (category_name, color_name)
    """
    t = TRANSLATIONS.get(lang, TRANSLATIONS["en"])

    if aqi <= 50:
        return (t["good"], "green")
    elif aqi <= 100:
        return (t["moderate"], "yellow")
    elif aqi <= 150:
        return (t["unhealthy_sensitive"], "orange")
    elif aqi <= 200:
        return (t["unhealthy"], "red")
    elif aqi <= 300:
        return (t["very_unhealthy"], "purple")
    else:
        return (t["hazardous"], "maroon")


def render_aqi_widget(
    city: str = "Tashkent",
    aqi: int = 235,
    category: str | None = None,
    scale: str = "US AQI",
    pollutant: str = "PM2.5",
    temp: str = "14°C",
    humidity: str = "41%",
    wind: str = "7 km/h",
    updated: str | None = None,
    lang: str = "ru",
) -> Card:
    """
    Render an AQI (Air Quality Index) widget.

    Args:
        city: City name
        aqi: Air Quality Index value
        category: AQI category description (auto-detected if None)
        scale: AQI scale type (US AQI, etc.)
        pollutant: Main pollutant
        temp: Temperature
        humidity: Humidity percentage
        wind: Wind speed
        updated: Last update time
        lang: Language code (ru, uz, en)
    """
    t = TRANSLATIONS.get(lang, TRANSLATIONS["en"])

    if updated is None:
        now = datetime.now()
        updated = now.strftime("%H:%M, %d %B")

    # Get category in the right language if not provided
    if category is None:
        category, _ = get_aqi_category(aqi, lang)

    # Header with title and scale badge
    header = Row(
        children=[
            Title(
                value=f"{t['title']} — {city}",
                size="sm"
            ),
            Spacer(),
            Badge(
                label=scale,
                variant="soft"
            ),
        ]
    )

    # Update time caption
    caption = Text(
        value=f"{t['updated']}: {updated}",
        size="sm",
        color="alpha-60"
    )

    # Main AQI display box with purple gradient
    main_aqi_box = Box(
        padding=3,
        radius="lg",
        background={"light": "purple-100", "dark": "purple-900"},
        children=[
            Row(
                gap=3,
                align="center",
                children=[
                    # Icon box
                    Box(
                        size=44,
                        radius="sm",
                        background={"light": "purple-400", "dark": "purple-600"},
                        align="center",
                        justify="center",
                        children=[
                            Icon(
                                name="lab",
                                color="white",
                                size="xl"
                            ),
                        ]
                    ),
                    # AQI value and category
                    Row(
                        gap=4,
                        align="center",
                        children=[
                            Title(
                                value=str(aqi),
                                size="3xl"
                            ),
                            Col(
                                gap=0,
                                children=[
                                    Text(
                                        value=category,
                                        weight="semibold"
                                    ),
                                    Badge(
                                        label=pollutant,
                                        variant="outline",
                                        color="discovery"
                                    ),
                                ]
                            ),
                        ]
                    ),
                ]
            ),
        ]
    )

    # Weather details row
    weather_details = Row(
        children=[
            Text(
                value=f"{t['temp']}: {temp}",
                size="sm"
            ),
            Spacer(),
            Text(
                value=f"{t['humidity']}: {humidity}",
                size="sm"
            ),
            Spacer(),
            Text(
                value=f"{t['wind']}: {wind}",
                size="sm"
            ),
        ]
    )

    # Build the complete widget (without refresh button)
    return Card(
        key="aqi-widget",
        size="md",
        children=[
            Col(
                gap=2,
                children=[
                    header,
                    caption,
                    main_aqi_box,
                    weather_details,
                ]
            )
        ]
    )


def aqi_widget_copy_text(
    city: str,
    aqi: int,
    category: str,
) -> str:
    """Generate copy text for the AQI widget."""
    return f"Air Quality in {city}: AQI {aqi} - {category}"
