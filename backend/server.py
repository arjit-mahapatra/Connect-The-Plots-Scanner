from fastapi import FastAPI, APIRouter, HTTPException, Depends, Body, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import uuid
import logging
import json
import random
from pathlib import Path
import requests
from datetime import datetime
import hashlib
import jwt
from passlib.context import CryptContext

# Setup 
ROOT_DIR = Path(__file__).parent
# Load .env but ONLY if the environment variables don't already exist
# This ensures Render's environment variables take precedence
load_dotenv(ROOT_DIR / '.env', override=False)

# MongoDB connection
import sys

# Get connection string from environment variable
try:
    # Check if we're in production or dev environment
    is_production = os.environ.get('RENDER', '') == 'true'
    
    if is_production:
        # In production, use the connection_string environment variable
        mongo_url = os.environ.get('connection_string')
        if not mongo_url:
            print("WARNING: 'connection_string' environment variable not found, falling back to MONGO_URL")
            mongo_url = os.environ.get('MONGO_URL')
            
        print(f"Using production MongoDB connection")
    else:
        # In dev, use MONGO_URL from .env file
        mongo_url = os.environ.get('MONGO_URL')
        print(f"Using development MongoDB connection")
    
    # Set a reasonable timeout for connection
    client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=10000)
    
    # This database name should match what you want to use in MongoDB Atlas
    db_name = os.environ.get('DB_NAME', 'stock_news_db')
    db = client[db_name]
    
    print(f"MongoDB connection successful to database: {db_name}")
except Exception as e:
    print(f"MongoDB connection error: {e}", file=sys.stderr)
    # In production, you might want to handle this more gracefully
    # sys.exit(1)  # Uncomment to exit on connection failure

# For Render deployment
PORT = int(os.environ.get("PORT", 8001))

# Create the main app
app = FastAPI(title="Stock Impact News Scanner")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# JWT settings
SECRET_KEY = os.environ.get("SECRET_KEY", "defaultsecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define Models
class NewsSource(BaseModel):
    name: str
    url: str
    reliability_score: float = 1.0

class Stock(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str
    name: str
    exchange: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class NewsItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    url: str
    source: str
    published_at: datetime
    category: str
    affected_stocks: List[str] = []
    confidence_score: float = 0.0
    validated_sources: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class StockImpact(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    news_id: str
    stock_id: str
    impact_score: float  # -1.0 to 1.0 (negative to positive impact)
    explanation: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    favorite_stocks: List[str] = []
    favorite_news: List[str] = []

class UserInDB(User):
    hashed_password: str

class ForumPost(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    username: str
    title: str
    content: str
    stocks: List[str] = []
    upvotes: int = 0
    comments: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Comment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    post_id: str
    user_id: str
    username: str
    content: str
    upvotes: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Auth helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def get_user(username: str):
    user_dict = await db.users.find_one({"username": username})
    if user_dict:
        return UserInDB(**user_dict)
    return None

async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except:
        raise credentials_exception
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# Mock news sources
mock_news_sources = [
    {"name": "Financial Times", "url": "https://ft.com", "reliability_score": 0.9},
    {"name": "Bloomberg", "url": "https://bloomberg.com", "reliability_score": 0.92},
    {"name": "CNBC", "url": "https://cnbc.com", "reliability_score": 0.85},
    {"name": "Reuters", "url": "https://reuters.com", "reliability_score": 0.93},
    {"name": "Wall Street Journal", "url": "https://wsj.com", "reliability_score": 0.91}
]

# Mock stocks
mock_stocks = [
    {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"},
    {"symbol": "GOOGL", "name": "Alphabet Inc.", "exchange": "NASDAQ"},
    {"symbol": "AMZN", "name": "Amazon.com Inc.", "exchange": "NASDAQ"},
    {"symbol": "TSLA", "name": "Tesla Inc.", "exchange": "NASDAQ"},
    {"symbol": "META", "name": "Meta Platforms Inc.", "exchange": "NASDAQ"},
    {"symbol": "MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ"},
    {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "exchange": "NYSE"},
    {"symbol": "V", "name": "Visa Inc.", "exchange": "NYSE"},
    {"symbol": "JNJ", "name": "Johnson & Johnson", "exchange": "NYSE"},
    {"symbol": "WMT", "name": "Walmart Inc.", "exchange": "NYSE"}
]

# Mock news headlines with impacts
mock_news = [
    {
        "title": "Federal Reserve announces unexpected 50 basis point rate hike",
        "content": "The Federal Reserve has announced a larger-than-expected interest rate increase of 50 basis points, citing persistent inflation concerns.",
        "url": "https://example.com/fed-rate-hike",
        "source": "Bloomberg",
        "published_at": datetime.utcnow() - timedelta(hours=3),
        "category": "Economy",
        "affected_stocks": ["JPM", "WMT", "AAPL"],
        "confidence_score": 0.87,
        "validated_sources": ["Bloomberg", "CNBC", "Reuters"]
    },
    {
        "title": "Apple unveils new AI features for iPhone 16",
        "content": "Apple has announced groundbreaking AI capabilities for its upcoming iPhone 16, potentially shifting the competitive landscape in mobile technology.",
        "url": "https://example.com/apple-ai",
        "source": "CNBC",
        "published_at": datetime.utcnow() - timedelta(hours=6),
        "category": "Technology",
        "affected_stocks": ["AAPL", "GOOGL", "MSFT"],
        "confidence_score": 0.95,
        "validated_sources": ["CNBC", "Reuters", "Wall Street Journal", "Financial Times"]
    },
    {
        "title": "Tesla faces battery supply chain disruptions from Southeast Asia",
        "content": "Tesla is experiencing significant supply chain challenges for battery components due to political instability in key Southeast Asian manufacturing countries.",
        "url": "https://example.com/tesla-supply-chain",
        "source": "Reuters",
        "published_at": datetime.utcnow() - timedelta(hours=12),
        "category": "Manufacturing",
        "affected_stocks": ["TSLA", "GM", "F"],
        "confidence_score": 0.78,
        "validated_sources": ["Reuters", "Bloomberg"]
    },
    {
        "title": "US and China announce new round of trade talks amid rising tensions",
        "content": "Officials from the United States and China have scheduled a high-level meeting to address trade disputes as tensions escalate over technology export restrictions.",
        "url": "https://example.com/us-china-trade",
        "source": "Financial Times",
        "published_at": datetime.utcnow() - timedelta(days=1),
        "category": "Geopolitics",
        "affected_stocks": ["AAPL", "TSLA", "WMT", "AMZN"],
        "confidence_score": 0.91,
        "validated_sources": ["Financial Times", "Wall Street Journal", "Bloomberg", "Reuters"]
    },
    {
        "title": "Amazon's AWS experiences major outage affecting banking services",
        "content": "Amazon Web Services is currently experiencing a significant outage across its US-East region, impacting numerous financial services and banking applications.",
        "url": "https://example.com/aws-outage",
        "source": "Wall Street Journal",
        "published_at": datetime.utcnow() - timedelta(hours=8),
        "category": "Technology",
        "affected_stocks": ["AMZN", "JPM", "V", "MSFT"],
        "confidence_score": 0.89,
        "validated_sources": ["Wall Street Journal", "CNBC"]
    }
]

# Sample explanations for stock impacts
mock_impacts = [
    {
        "news_id": "",  # Will be set when news is created
        "stock_id": "",  # Will be set when stocks are created
        "stock_symbol": "AAPL",
        "news_title": "Federal Reserve announces unexpected 50 basis point rate hike",
        "impact_score": -0.7,
        "explanation": "The larger-than-expected rate hike is likely to negatively impact Apple due to potentially reduced consumer spending on high-end electronics and increased borrowing costs for the company."
    },
    {
        "news_id": "",
        "stock_id": "",
        "stock_symbol": "JPM",
        "news_title": "Federal Reserve announces unexpected 50 basis point rate hike",
        "impact_score": 0.4,
        "explanation": "JPMorgan Chase may see a positive impact from the rate hike as higher interest rates typically expand banking margins on loans, potentially increasing profitability."
    },
    {
        "news_id": "",
        "stock_id": "",
        "stock_symbol": "AAPL",
        "news_title": "Apple unveils new AI features for iPhone 16",
        "impact_score": 0.9,
        "explanation": "The announcement of groundbreaking AI features for the iPhone 16 is highly positive for Apple as it demonstrates continued innovation leadership and creates a compelling reason for consumers to upgrade their devices."
    },
    {
        "news_id": "",
        "stock_id": "",
        "stock_symbol": "TSLA",
        "news_title": "Tesla faces battery supply chain disruptions from Southeast Asia",
        "impact_score": -0.8,
        "explanation": "The supply chain disruptions could significantly hamper Tesla's production capacity and delivery targets, potentially leading to reduced revenue and increased costs in the short to medium term."
    }
]

# Mock user data
mock_users = [
    {
        "email": "john@example.com",
        "username": "john_doe",
        "password": "password123",
        "favorite_stocks": ["AAPL", "MSFT"],
        "favorite_news": []
    },
    {
        "email": "jane@example.com",
        "username": "jane_smith",
        "password": "password456",
        "favorite_stocks": ["TSLA", "AMZN"],
        "favorite_news": []
    }
]

# Mock forum posts
mock_posts = [
    {
        "user_id": "",  # Will be set when users are created
        "username": "john_doe",
        "title": "How to trade the Fed rate hike?",
        "content": "I think banking stocks will benefit from the recent Fed decision. What do you all think?",
        "stocks": ["JPM", "V"],
        "upvotes": 15,
        "comments": []
    },
    {
        "user_id": "",  # Will be set when users are created
        "username": "jane_smith",
        "title": "Tesla supply chain issues - buy the dip?",
        "content": "With the recent news about Tesla's supply chain problems, the stock might dip. Is this a buying opportunity or a warning sign?",
        "stocks": ["TSLA"],
        "upvotes": 8,
        "comments": []
    }
]

# Mock comments
mock_comments = [
    {
        "post_id": "",  # Will be set when posts are created
        "user_id": "",  # Will be set when users are created
        "username": "jane_smith",
        "content": "I agree, banking stocks usually benefit from rate hikes. I'm also looking at insurance companies.",
        "upvotes": 5
    },
    {
        "post_id": "",  # Will be set when posts are created
        "user_id": "",  # Will be set when users are created
        "username": "john_doe",
        "content": "I'm cautious about Tesla. The supply chain issues could persist longer than expected.",
        "upvotes": 3
    }
]

# Mock function for LLM analysis
def analyze_news_impact(news_item, stock):
    """
    Mock LLM function to analyze impact of news on a stock
    This will be replaced with actual LLM integration
    """
    # Check if we have a pre-defined impact for this news-stock combination
    for impact in mock_impacts:
        if impact["stock_symbol"] == stock["symbol"] and impact["news_title"] == news_item["title"]:
            return {
                "impact_score": impact["impact_score"],
                "explanation": impact["explanation"]
            }
    
    # Generate a random impact if no pre-defined one exists
    random_impact = random.uniform(-1.0, 1.0)
    explanation = f"This news might {'positively' if random_impact > 0 else 'negatively'} impact {stock['name']} due to potential market sentiment shifts."
    
    return {
        "impact_score": random_impact,
        "explanation": explanation
    }

# DB initialization function
async def init_db():
    try:
        # Create indexes
        logger.info("Creating database indexes...")
        await db.news.create_index("title")
        await db.stocks.create_index("symbol", unique=True)
        await db.users.create_index("username", unique=True)
        await db.users.create_index("email", unique=True)
        
        # Initialize mock data if needed
        logger.info("Checking if stock data initialization is needed...")
        if await db.stocks.count_documents({}) == 0:
            logger.info("Initializing stocks collection with mock data...")
            await db.stocks.insert_many(mock_stocks)
            logger.info("Initialized stocks collection with mock data")
        else:
            logger.info("Stocks collection already contains data, skipping initialization")
        
        logger.info("Checking if news sources initialization is needed...")
        if await db.news_sources.count_documents({}) == 0:
            logger.info("Initializing news sources collection with mock data...")
            await db.news_sources.insert_many(mock_news_sources)
            logger.info("Initialized news sources collection with mock data")
        else:
            logger.info("News sources collection already contains data, skipping initialization")
        
        # Get stock IDs for reference
        logger.info("Fetching stock data for reference...")
        stocks = {stock["symbol"]: stock for stock in await db.stocks.find().to_list(1000)}
        
        # Create news items if none exist
        logger.info("Checking if news data initialization is needed...")
        if await db.news.count_documents({}) == 0:
            logger.info("Initializing news collection with mock data...")
            for news_item in mock_news:
                news_id = str(uuid.uuid4())
                news_item["id"] = news_id
                await db.news.insert_one(news_item)
                
                # Create impact records for affected stocks
                for symbol in news_item["affected_stocks"]:
                    if symbol in stocks:
                        stock = stocks[symbol]
                        impact_analysis = analyze_news_impact(news_item, stock)
                        
                        impact = {
                            "id": str(uuid.uuid4()),
                            "news_id": news_id,
                            "stock_id": stock["id"] if "id" in stock else "",
                            "impact_score": impact_analysis["impact_score"],
                            "explanation": impact_analysis["explanation"],
                            "created_at": datetime.utcnow()
                        }
                        
                        await db.stock_impacts.insert_one(impact)
            
            logger.info("Initialized news collection with mock data")
        else:
            logger.info("News collection already contains data, skipping initialization")
        
        # Create users if none exist
        logger.info("Checking if user data initialization is needed...")
        user_ids = {}
        if await db.users.count_documents({}) == 0:
            logger.info("Initializing users collection with mock data...")
            for user_data in mock_users:
                user_id = str(uuid.uuid4())
                hashed_password = get_password_hash(user_data["password"])
                
                user = {
                    "id": user_id,
                    "email": user_data["email"],
                    "username": user_data["username"],
                    "hashed_password": hashed_password,
                    "favorite_stocks": user_data["favorite_stocks"],
                    "favorite_news": user_data["favorite_news"],
                    "created_at": datetime.utcnow()
                }
                
                await db.users.insert_one(user)
                user_ids[user_data["username"]] = user_id
            
            logger.info("Initialized users collection with mock data")
        else:
            logger.info("Users collection already contains data, skipping initialization")
            # Get existing user IDs for forum posts
            async for user in db.users.find({}, {"username": 1, "id": 1}):
                if "username" in user and "id" in user:
                    user_ids[user["username"]] = user["id"]
        
        # Create forum posts if none exist
        logger.info("Checking if forum posts initialization is needed...")
        if await db.forum_posts.count_documents({}) == 0:
            logger.info("Initializing forum posts and comments with mock data...")
            for post_data in mock_posts:
                post_id = str(uuid.uuid4())
                
                # Set user_id if available
                if post_data["username"] in user_ids:
                    post_data["user_id"] = user_ids[post_data["username"]]
                
                post_data["id"] = post_id
                await db.forum_posts.insert_one(post_data)
                
                # Create associated comments
                for comment in mock_comments:
                    # Only create comments if they don't exist yet
                    existing_comment = await db.comments.find_one({"post_id": post_id, "username": comment["username"]})
                    
                    if not existing_comment:
                        if comment["username"] in user_ids:
                            comment["user_id"] = user_ids[comment["username"]]
                        
                        comment["post_id"] = post_id
                        comment["id"] = str(uuid.uuid4())
                        
                        await db.comments.insert_one(comment)
                        
                        # Add comment ID to post's comments list
                        await db.forum_posts.update_one(
                            {"id": post_id},
                            {"$push": {"comments": comment["id"]}}
                        )
            
            logger.info("Initialized forum posts and comments with mock data")
        else:
            logger.info("Forum posts collection already contains data, skipping initialization")
        
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Error during database initialization: {str(e)}")
        print(f"Error during database initialization: {str(e)}", file=sys.stderr)
        # Continue with application startup even if initialization fails
        # In production, you might want to handle this differently

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Welcome to the Stock Impact News Scanner API"}

# News Routes
@api_router.get("/news", response_model=List[NewsItem])
async def get_news(limit: int = 10, skip: int = 0, category: Optional[str] = None):
    query = {} if category is None else {"category": category}
    news = await db.news.find(query).sort("published_at", -1).skip(skip).limit(limit).to_list(limit)
    return news

@api_router.get("/news/{news_id}", response_model=NewsItem)
async def get_news_item(news_id: str):
    news = await db.news.find_one({"id": news_id})
    if news is None:
        raise HTTPException(status_code=404, detail="News item not found")
    return news

@api_router.get("/news/{news_id}/impacts", response_model=List[StockImpact])
async def get_news_impacts(news_id: str):
    impacts = await db.stock_impacts.find({"news_id": news_id}).to_list(1000)
    if not impacts:
        raise HTTPException(status_code=404, detail="No impacts found for this news item")
    return impacts

# Stock Routes
@api_router.get("/stocks", response_model=List[Stock])
async def get_stocks(limit: int = 100, exchange: Optional[str] = None):
    query = {} if exchange is None else {"exchange": exchange}
    stocks = await db.stocks.find(query).limit(limit).to_list(limit)
    return stocks

@api_router.get("/stocks/{stock_id}", response_model=Stock)
async def get_stock(stock_id: str):
    stock = await db.stocks.find_one({"id": stock_id})
    if stock is None:
        # Try finding by symbol
        stock = await db.stocks.find_one({"symbol": stock_id})
        if stock is None:
            raise HTTPException(status_code=404, detail="Stock not found")
    return stock

@api_router.get("/stocks/{stock_id}/news", response_model=List[NewsItem])
async def get_stock_news(stock_id: str, limit: int = 10):
    stock = await db.stocks.find_one({"id": stock_id})
    if stock is None:
        # Try finding by symbol
        stock = await db.stocks.find_one({"symbol": stock_id})
        if stock is None:
            raise HTTPException(status_code=404, detail="Stock not found")
    
    # Find news that affects this stock
    symbol = stock["symbol"]
    news = await db.news.find({"affected_stocks": symbol}).sort("published_at", -1).limit(limit).to_list(limit)
    return news

# User Routes
@api_router.post("/users", response_model=User)
async def create_user(user: UserCreate):
    # Check if username or email already exists
    if await db.users.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already registered")
    if await db.users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    user_dict = user.dict()
    user_dict.pop("password")
    user_dict["id"] = str(uuid.uuid4())
    user_dict["hashed_password"] = hashed_password
    user_dict["created_at"] = datetime.utcnow()
    user_dict["favorite_stocks"] = []
    user_dict["favorite_news"] = []
    
    await db.users.insert_one(user_dict)
    return User(**user_dict)

@api_router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@api_router.post("/users/me/favorite-stocks/{stock_id}")
async def add_favorite_stock(stock_id: str, current_user: User = Depends(get_current_user)):
    stock = await db.stocks.find_one({"id": stock_id})
    if stock is None:
        # Try finding by symbol
        stock = await db.stocks.find_one({"symbol": stock_id})
        if stock is None:
            raise HTTPException(status_code=404, detail="Stock not found")
    
    symbol = stock["symbol"]
    
    # Add to favorites if not already there
    result = await db.users.update_one(
        {"id": current_user.id, "favorite_stocks": {"$ne": symbol}},
        {"$push": {"favorite_stocks": symbol}}
    )
    
    if result.modified_count == 0:
        return {"message": "Stock already in favorites"}
    return {"message": f"Added {symbol} to favorites"}

@api_router.delete("/users/me/favorite-stocks/{stock_id}")
async def remove_favorite_stock(stock_id: str, current_user: User = Depends(get_current_user)):
    stock = await db.stocks.find_one({"id": stock_id})
    symbol = stock["symbol"] if stock else stock_id
    
    result = await db.users.update_one(
        {"id": current_user.id},
        {"$pull": {"favorite_stocks": symbol}}
    )
    
    if result.modified_count == 0:
        return {"message": "Stock not in favorites"}
    return {"message": f"Removed {symbol} from favorites"}

# Forum Routes
@api_router.get("/forum/posts", response_model=List[ForumPost])
async def get_forum_posts(limit: int = 20, skip: int = 0):
    posts = await db.forum_posts.find().sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    return posts

@api_router.post("/forum/posts", response_model=ForumPost)
async def create_forum_post(
    title: str = Body(...),
    content: str = Body(...),
    stocks: List[str] = Body([]),
    current_user: User = Depends(get_current_user)
):
    post = ForumPost(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        username=current_user.username,
        title=title,
        content=content,
        stocks=stocks,
        upvotes=0,
        comments=[],
        created_at=datetime.utcnow()
    )
    
    await db.forum_posts.insert_one(post.dict())
    return post

@api_router.get("/forum/posts/{post_id}", response_model=ForumPost)
async def get_forum_post(post_id: str):
    post = await db.forum_posts.find_one({"id": post_id})
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@api_router.post("/forum/posts/{post_id}/comments", response_model=Comment)
async def add_comment(
    post_id: str,
    content: str = Body(...),
    current_user: User = Depends(get_current_user)
):
    post = await db.forum_posts.find_one({"id": post_id})
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    comment = Comment(
        id=str(uuid.uuid4()),
        post_id=post_id,
        user_id=current_user.id,
        username=current_user.username,
        content=content,
        upvotes=0,
        created_at=datetime.utcnow()
    )
    
    await db.comments.insert_one(comment.dict())
    
    # Add comment ID to post's comments list
    await db.forum_posts.update_one(
        {"id": post_id},
        {"$push": {"comments": comment.id}}
    )
    
    return comment

@api_router.get("/forum/posts/{post_id}/comments", response_model=List[Comment])
async def get_post_comments(post_id: str):
    post = await db.forum_posts.find_one({"id": post_id})
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    comments = await db.comments.find({"post_id": post_id}).sort("created_at", 1).to_list(1000)
    return comments

@api_router.post("/forum/posts/{post_id}/upvote")
async def upvote_post(post_id: str, current_user: User = Depends(get_current_user)):
    result = await db.forum_posts.update_one({"id": post_id}, {"$inc": {"upvotes": 1}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post upvoted successfully"}

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    try:
        logger.info("Starting application initialization...")
        logger.info("Testing MongoDB connection...")
        # Just a basic command to verify connection works
        await client.admin.command('ping')
        logger.info("MongoDB connection test successful")
        
        # Initialize database
        await init_db()
        logger.info("Database initialization completed")
    except Exception as e:
        logger.error(f"Error during application startup: {str(e)}")
        print(f"APPLICATION STARTUP ERROR: {str(e)}", file=sys.stderr)
        # In production, you might want to exit here
        # But for now, we'll continue to allow the application to start
        # Even with DB issues so we can at least debug

# Include the router in the main app
app.include_router(api_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shutdown event
@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    logger.info("Database connection closed")
