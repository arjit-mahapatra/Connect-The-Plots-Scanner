from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os
import random
import requests
import datetime
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

# Add middleware for security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    # Allow JavaScript execution
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https:;"
    # Other security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# We'll move the root endpoint to /api to avoid conflicts with the frontend
@app.get("/api")
async def api_root():
    return {"message": "Welcome to the Stock News Scanner API", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Health check endpoint for Render"""
    return {"status": "healthy", "timestamp": datetime.datetime.now().isoformat()}

@app.get("/api/newsapi/top-headlines")
async def get_top_headlines(category: str = "business", country: str = "us"):
    try:
        if not NEWS_API_KEY:
            # Return mock data if no API key is provided
            return {
                "status": "ok",
                "totalResults": 2,
                "articles": [
                    {
                        "source": {"id": "mock-source", "name": "Mock News"},
                        "author": "Mock Author",
                        "title": "Mock Business Headline 1",
                        "description": "This is a mock business headline because the NEWS_API_KEY environment variable is not set.",
                        "url": "https://example.com/mock-news-1",
                        "urlToImage": "https://example.com/mock-image-1.jpg",
                        "publishedAt": datetime.datetime.now().isoformat(),
                        "content": "This is mock content. Please set the NEWS_API_KEY environment variable in the Render dashboard."
                    },
                    {
                        "source": {"id": "mock-source", "name": "Mock News"},
                        "author": "Mock Author",
                        "title": "Mock Business Headline 2",
                        "description": "This is another mock business headline because the NEWS_API_KEY environment variable is not set.",
                        "url": "https://example.com/mock-news-2",
                        "urlToImage": "https://example.com/mock-image-2.jpg",
                        "publishedAt": (datetime.datetime.now() - datetime.timedelta(hours=1)).isoformat(),
                        "content": "This is mock content. Please set the NEWS_API_KEY environment variable in the Render dashboard."
                    }
                ]
            }
        
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
        if not NEWS_API_KEY:
            # Return mock data if no API key is provided
            return {
                "status": "ok",
                "totalResults": 2,
                "articles": [
                    {
                        "source": {"id": "mock-source", "name": "Mock News"},
                        "author": "Mock Author",
                        "title": f"Mock Search Result for '{q}' 1",
                        "description": "This is a mock search result because the NEWS_API_KEY environment variable is not set.",
                        "url": "https://example.com/mock-search-1",
                        "urlToImage": "https://example.com/mock-image-1.jpg",
                        "publishedAt": datetime.datetime.now().isoformat(),
                        "content": "This is mock content. Please set the NEWS_API_KEY environment variable in the Render dashboard."
                    },
                    {
                        "source": {"id": "mock-source", "name": "Mock News"},
                        "author": "Mock Author",
                        "title": f"Mock Search Result for '{q}' 2",
                        "description": "This is another mock search result because the NEWS_API_KEY environment variable is not set.",
                        "url": "https://example.com/mock-search-2",
                        "urlToImage": "https://example.com/mock-image-2.jpg",
                        "publishedAt": (datetime.datetime.now() - datetime.timedelta(hours=1)).isoformat(),
                        "content": "This is mock content. Please set the NEWS_API_KEY environment variable in the Render dashboard."
                    }
                ]
            }
            
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
        # Stock names and price ranges for more realistic mock data
        stock_info = {
            "AAPL": {"name": "Apple Inc.", "min": 150, "max": 200},
            "GOOGL": {"name": "Alphabet Inc.", "min": 120, "max": 150},
            "MSFT": {"name": "Microsoft Corp.", "min": 300, "max": 350},
            "AMZN": {"name": "Amazon.com Inc.", "min": 120, "max": 150},
            "TSLA": {"name": "Tesla Inc.", "min": 150, "max": 200},
            "META": {"name": "Meta Platforms Inc.", "min": 300, "max": 350},
            "NVDA": {"name": "NVIDIA Corp.", "min": 700, "max": 800},
            "JPM": {"name": "JPMorgan Chase & Co.", "min": 150, "max": 200},
            "V": {"name": "Visa Inc.", "min": 230, "max": 280},
            "JNJ": {"name": "Johnson & Johnson", "min": 150, "max": 180}
        }
        
        # Use stock-specific price range if available, otherwise use default
        info = stock_info.get(symbol, {"name": symbol, "min": 50, "max": 500})
        
        # Mock stock data
        mock_data = {
            "symbol": symbol,
            "name": info["name"],
            "price": round(random.uniform(info["min"], info["max"]), 2),
            "change": round(random.uniform(-5, 5), 2)
        }
        return mock_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Define all API routes first before mounting static files

# Mount static files for frontend
frontend_build_dir = Path(__file__).parent.parent / "frontend" / "build"
print(f"Looking for frontend build directory at: {frontend_build_dir}")
print(f"Frontend build directory exists: {frontend_build_dir.exists()}")
print(f"Contents of parent directory: {list(frontend_build_dir.parent.iterdir())}")

# Check if frontend build directory exists
if frontend_build_dir.exists():
    print(f"Frontend build directory contents: {list(frontend_build_dir.iterdir())}")
    # Mount static files directory - make sure to serve all static files, not just the /static directory
    app.mount("/static", StaticFiles(directory=str(frontend_build_dir / "static")), name="static")
    # Also mount any other static files at the root level
    for item in frontend_build_dir.iterdir():
        if item.is_file() and item.name != "index.html":
            print(f"Mounting static file: {item.name}")
            @app.get(f"/{item.name}")
            async def serve_static_file(item=item):
                return FileResponse(str(item))
    
    # Add a route to serve index.html at the root
    @app.get("/")
    async def serve_root():
        return FileResponse(str(frontend_build_dir / "index.html"))
    
    # Add a route to serve asset-manifest.json
    @app.get("/asset-manifest.json")
    async def serve_manifest():
        return FileResponse(str(frontend_build_dir / "asset-manifest.json"))
    
    # Catch-all route for SPA routing
    @app.get("/{full_path:path}")
    async def serve_frontend(request: Request, full_path: str):
        # Skip API routes
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not Found")
            
        # Try to serve the file directly if it exists
        file_path = frontend_build_dir / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
            
        # Otherwise serve index.html for client-side routing
        return FileResponse(str(frontend_build_dir / "index.html"))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
