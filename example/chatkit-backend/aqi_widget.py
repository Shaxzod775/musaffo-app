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
    Button,
    Card,
    Col,
    Icon,
    Row,
    Spacer,
    Text,
    Title,
)


def get_aqi_category(aqi: int) -> tuple[str, str]:
    """
    Get AQI category and color based on value.

    Args:
        aqi: Air Quality Index value

    Returns:
        Tuple of (category_name, color_name)
    """
    if aqi <= 50:
        return ("Хорошо", "green")
    elif aqi <= 100:
        return ("Умеренно", "yellow")
    elif aqi <= 150:
        return ("Вредно для чувствительных", "orange")
    elif aqi <= 200:
        return ("Вредно", "red")
    elif aqi <= 300:
        return ("Очень вредно", "purple")
    else:
        return ("Опасно", "maroon")


def render_aqi_widget(
    city: str = "Ташкент",
    aqi: int = 235,
    category: str = "Очень вредно",
    scale: str = "US AQI",
    pollutant: str = "PM2.5",
    temp: str = "14°C",
    humidity: str = "41%",
    wind: str = "7 км/ч",
    updated: str | None = None,
) -> Card:
    """
    Render an AQI (Air Quality Index) widget.

    Args:
        city: City name
        aqi: Air Quality Index value
        category: AQI category description
        scale: AQI scale type (US AQI, etc.)
        pollutant: Main pollutant
        temp: Temperature
        humidity: Humidity percentage
        wind: Wind speed
        updated: Last update time
    """
    if updated is None:
        now = datetime.now()
        updated = now.strftime("%H:%M, %d %B")

    # Determine color based on AQI
    _, aqi_color = get_aqi_category(aqi)

    # Header with title and scale badge
    header = Row(
        children=[
            Title(
                value=f"Качество воздуха — {city}",
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
        value=f"Обновлено: {updated}",
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
                value=f"Темп.: {temp}",
                size="sm"
            ),
            Spacer(),
            Text(
                value=f"Влажн.: {humidity}",
                size="sm"
            ),
            Spacer(),
            Text(
                value=f"Ветер: {wind}",
                size="sm"
            ),
        ]
    )

    # Refresh button with action to re-fetch AQI data
    refresh_button = Row(
        children=[
            Button(
                label="Обновить",
                icon_start="reload",
                variant="outline",
            )
        ]
    )

    # Build the complete widget
    return Card(
        key="aqi-tashkent",
        size="md",
        children=[
            Col(
                gap=2,
                children=[
                    header,
                    caption,
                    main_aqi_box,
                    weather_details,
                    refresh_button,
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
