from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import random
import requests
from pathlib import Path

# Setup
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env', override=False)

# NewsAPI setup
NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
NEWS_API_URL = "https://newsapi.org/v2"

# Create the main app
app = FastAPI(title="Stock News Scanner")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Stock News Scanner API"}

@app.get("/api/newsapi/top-headlines")
async def get_top_headlines(category: str = "business", country: str = "us"):
    try:
        url = f"{NEWS_API_URL}/top-headlines"
        params = {
            "apiKey": NEWS_API_KEY,
            "category": category,
            "country": country
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/newsapi/everything")
async def get_everything(q: str, sortBy: str = "publishedAt", language: str = "en"):
    try:
        url = f"{NEWS_API_URL}/everything"
        params = {
            "apiKey": NEWS_API_KEY,
            "q": q,
            "sortBy": sortBy,
            "language": language
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stock/{symbol}")
async def get_stock_data(symbol: str):
    try:
        # Mock stock data
        mock_data = {
            "symbol": symbol,
            "price": round(random.uniform(50, 500), 2),
            "change": round(random.uniform(-5, 5), 2)
        }
        return mock_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
