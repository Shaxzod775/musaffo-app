from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Import routes
from app.routes import news, donations, voting, reports, projects, aqi, stats

load_dotenv()

app = FastAPI(
    title="Musaffo API",
    description="Backend API for Musaffo Air Quality & Eco Fund",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(news.router)
app.include_router(donations.router)
app.include_router(voting.router)
app.include_router(reports.router)
app.include_router(projects.router)
app.include_router(aqi.router)
app.include_router(stats.router)

@app.get("/")
async def root():
    return {
        "message": "Musaffo API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
