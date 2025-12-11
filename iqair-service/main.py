"""
IQAir Service - Microservice for air quality data
Fetches and caches AQI data from IQAir API
"""

import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="IQAir Service", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# IQAir API configuration
IQAIR_API_KEY = os.getenv("IQAIR_API_KEY")
IQAIR_BASE_URL = "https://api.airvisual.com/v2"

# In-memory cache
_cache: Dict[str, Any] = {}
_cache_timestamp: Optional[datetime] = None
CACHE_TTL_MINUTES = 10


def get_health_risks(aqi: int) -> dict:
    """Generate health risk information based on AQI level"""
    if aqi <= 50:
        return {
            "level": "good",
            "warning_ru": "Воздух чистый",
            "warning_uz": "Havo toza",
            "warning_en": "Air is clean",
            "affected_groups": [],
            "severity": "low"
        }
    elif aqi <= 100:
        return {
            "level": "moderate",
            "warning_ru": "Чувствительным людям стоит быть осторожнее",
            "warning_uz": "Sezgir odamlar ehtiyot bo'lishi kerak",
            "warning_en": "Sensitive people should be cautious",
            "affected_groups": ["asthmatics", "children"],
            "severity": "low"
        }
    elif aqi <= 150:
        return {
            "level": "unhealthy_sensitive",
            "warning_ru": "Вредно для уязвимых групп",
            "warning_uz": "Zaif guruhlar uchun zararli",
            "warning_en": "Unhealthy for sensitive groups",
            "affected_groups": ["children", "elderly", "asthmatics", "heart_patients"],
            "severity": "medium"
        }
    elif aqi <= 200:
        return {
            "level": "unhealthy",
            "warning_ru": "Вредно для всех. Носите респиратор",
            "warning_uz": "Hamma uchun zararli. Respirator taqdiring",
            "warning_en": "Unhealthy for everyone. Wear a respirator",
            "affected_groups": ["everyone"],
            "severity": "high"
        }
    elif aqi <= 300:
        return {
            "level": "very_unhealthy",
            "warning_ru": "Очень вредно! Избегайте выхода на улицу",
            "warning_uz": "Juda zararli! Tashqariga chiqmang",
            "warning_en": "Very unhealthy! Avoid going outside",
            "affected_groups": ["everyone"],
            "severity": "very_high"
        }
    else:
        return {
            "level": "hazardous",
            "warning_ru": "ОПАСНО ДЛЯ ЖИЗНИ! Оставайтесь дома",
            "warning_uz": "HAYOT UCHUN XAVFLI! Uyda qoling",
            "warning_en": "HAZARDOUS! Stay indoors",
            "affected_groups": ["everyone"],
            "severity": "extreme"
        }


@app.get("/")
async def root():
    return {"service": "IQAir Service", "status": "running"}


@app.get("/api/air-quality")
async def get_air_quality(city: str = "Tashkent", country: str = "Uzbekistan", state: str = "Toshkent Shahri"):
    """
    Get air quality data with caching and health risks
    """
    global _cache, _cache_timestamp
    
    # Check cache
    cache_key = f"{city}_{country}"
    if _cache_timestamp and datetime.now() - _cache_timestamp < timedelta(minutes=CACHE_TTL_MINUTES):
        if cache_key in _cache:
            cached_data = _cache[cache_key]
            pollution = cached_data.get("current", {}).get("pollution", {})
            aqi = pollution.get("aqius", 0)
            main_pollutant = pollution.get("mainus", "p2")
            health_risks = get_health_risks(aqi)
            
            # Calculate pollutants for cache
            pollutants = {
                "pm25": None,
                "pm10": None,
                "no2": None,
                "mainPollutant": main_pollutant
            }
            
            if main_pollutant == "p2":
                pollutants["pm25"] = round(aqi * 0.5)
                pollutants["pm10"] = round(aqi * 0.7)
                pollutants["no2"] = round(aqi * 0.3)
            elif main_pollutant == "p1":
                pollutants["pm10"] = round(aqi * 0.8)
                pollutants["pm25"] = round(aqi * 0.4)
                pollutants["no2"] = round(aqi * 0.3)
            elif main_pollutant == "n2":
                pollutants["no2"] = round(aqi * 0.6)
                pollutants["pm25"] = round(aqi * 0.3)
                pollutants["pm10"] = round(aqi * 0.5)
            else:
                pollutants["pm25"] = round(aqi * 0.4)
                pollutants["pm10"] = round(aqi * 0.6)
                pollutants["no2"] = round(aqi * 0.3)
            
            return {
                "status": "success",
                "source": "cache",
                "data": cached_data,
                "healthRisks": health_risks,
                "pollutants": pollutants,
                "cached_at": _cache_timestamp.isoformat()
            }
    
    # Fetch from IQAir API
    if not IQAIR_API_KEY or IQAIR_API_KEY == 'your_iqair_api_key_here':
        logger.warning("IQAir API key not configured, using fallback data")
        # Use fallback data
        fallback_data = {
            'current': {
                'pollution': {'aqius': 165, 'mainus': 'p2'},
                'weather': {'tp': 15, 'hu': 45}
            },
            'city': city,
            'state': city,
            'country': country,
            'location': {'coordinates': [69.2401, 41.2995]}
        }
        health_risks = get_health_risks(165)
        pollutants = {
            "pm25": 66,  # 165 * 0.4
            "pm10": 99,  # 165 * 0.6
            "no2": 50,   # 165 * 0.3
            "mainPollutant": "p2"
        }
        return {
            "status": "success",
            "source": "fallback",
            "data": fallback_data,
            "healthRisks": health_risks,
            "pollutants": pollutants,
            "warning": "API key not configured"
        }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{IQAIR_BASE_URL}/city",
                params={
                    "city": city,
                    "state": state,
                    "country": country,
                    "key": IQAIR_API_KEY
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    data = result.get("data", {})
                    
                    # Cache the result
                    _cache[cache_key] = data
                    _cache_timestamp = datetime.now()
                    
                    # Get health risks and pollutant details
                    pollution = data.get("current", {}).get("pollution", {})
                    aqi = pollution.get("aqius", 0)
                    main_pollutant = pollution.get("mainus", "p2")
                    
                    health_risks = get_health_risks(aqi)
                    
                    # Extract pollutant values based on main pollutant type
                    # IQAir returns main pollutant type: p2 (PM2.5), p1 (PM10), o3 (Ozone), n2 (NO2), s2 (SO2), co (CO)
                    pollutants = {
                        "pm25": None,
                        "pm10": None,
                        "no2": None,
                        "mainPollutant": main_pollutant
                    }
                    
                    # Since IQAir doesn't return individual pollutant values in free API,
                    # we estimate based on AQI and main pollutant type
                    if main_pollutant == "p2":  # PM2.5 is main pollutant
                        pollutants["pm25"] = round(aqi * 0.5)  # Rough conversion
                        pollutants["pm10"] = round(aqi * 0.7)
                        pollutants["no2"] = round(aqi * 0.3)
                    elif main_pollutant == "p1":  # PM10 is main pollutant
                        pollutants["pm10"] = round(aqi * 0.8)
                        pollutants["pm25"] = round(aqi * 0.4)
                        pollutants["no2"] = round(aqi * 0.3)
                    elif main_pollutant == "n2":  # NO2 is main pollutant
                        pollutants["no2"] = round(aqi * 0.6)
                        pollutants["pm25"] = round(aqi * 0.3)
                        pollutants["pm10"] = round(aqi * 0.5)
                    else:  # Default estimation
                        pollutants["pm25"] = round(aqi * 0.4)
                        pollutants["pm10"] = round(aqi * 0.6)
                        pollutants["no2"] = round(aqi * 0.3)
                    
                    return {
                        "status": "success",
                        "source": "api",
                        "data": data,
                        "healthRisks": health_risks,
                        "pollutants": pollutants
                    }
            
            # API error - return fallback
            logger.error(f"IQAir API error: {response.status_code}")
            fallback_data = {
                'current': {
                    'pollution': {'aqius': 165, 'mainus': 'p2'},
                    'weather': {'tp': 15, 'hu': 45}
                },
                'city': city,
                'state': city,
                'country': country,
                'location': {'coordinates': [69.2401, 41.2995]}
            }
            health_risks = get_health_risks(165)
            pollutants = {
                "pm25": 66,
                "pm10": 99,
                "no2": 50,
                "mainPollutant": "p2"
            }
            return {
                "status": "success",
                "source": "fallback",
                "data": fallback_data,
                "healthRisks": health_risks,
                "pollutants": pollutants,
                "warning": f"API returned {response.status_code}"
            }
            
    except httpx.TimeoutException:
        logger.error("IQAir API timeout")
        fallback_data = {
            'current': {
                'pollution': {'aqius': 165, 'mainus': 'p2'},
                'weather': {'tp': 15, 'hu': 45}
            },
            'city': city,
            'state': city,
            'country': country,
            'location': {'coordinates': [69.2401, 41.2995]}
        }
        health_risks = get_health_risks(165)
        pollutants = {
            "pm25": 66,
            "pm10": 99,
            "no2": 50,
            "mainPollutant": "p2"
        }
        return {
            "status": "success",
            "source": "fallback",
            "data": fallback_data,
            "healthRisks": health_risks,
            "pollutants": pollutants,
            "warning": "API timeout"
        }
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        fallback_data = {
            'current': {
                'pollution': {'aqius': 165, 'mainus': 'p2'},
                'weather': {'tp': 15, 'hu': 45}
            },
            'city': city,
            'state': city,
            'country': country,
            'location': {'coordinates': [69.2401, 41.2995]}
        }
        health_risks = get_health_risks(165)
        pollutants = {
            "pm25": 66,
            "pm10": 99,
            "no2": 50,
            "mainPollutant": "p2"
        }
        return {
            "status": "success",
            "source": "fallback",
            "data": fallback_data,
            "healthRisks": health_risks,
            "pollutants": pollutants,
            "warning": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8002))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
