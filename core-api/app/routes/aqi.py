from fastapi import APIRouter, HTTPException
import httpx
import os

router = APIRouter(prefix="/api/air-quality", tags=["air-quality"])

# IQAir service URL
IQAIR_SERVICE_URL = os.getenv('IQAIR_SERVICE_URL', 'http://localhost:8002')


@router.get("")
async def get_air_quality(city: str = "Tashkent", country: str = "Uzbekistan", state: str = "Toshkent Shahri"):
    """
    Proxy to iqair-service microservice
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{IQAIR_SERVICE_URL}/api/air-quality",
                params={"city": city, "country": country, "state": state}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"IQAir service error: {response.text}"
                )
                
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="IQAir service timeout")
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"IQAir service unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
