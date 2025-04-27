# StockNewsScanner 📈📰

A sophisticated web application that scans financial news from multiple sources to identify stocks potentially affected by current geopolitical, economic, and social developments.

## Overview

StockNewsScanner aggregates news from various financial platforms, validates information across multiple sources, and uses AI to explain potential impacts on relevant stocks. The application provides confidence scores based on cross-source validation and offers a community forum for users to discuss trading strategies.

![StockNewsScanner Screenshot](https://github.com/yourusername/stocknewsscanner/raw/main/screenshot.png)

## Features

### News Analysis
- **Multi-Source Aggregation**: Collects financial news from various reputable sources
- **Cross-Validation**: Verifies news across multiple sources to increase confidence
- **AI-Powered Analysis**: Explains potential impacts on stocks (requires API key)
- **Confidence Scoring**: Ranks news reliability based on source validation

### Stock Impact Assessment
- **Global Market Coverage**: Covers all major stock exchanges worldwide
- **Impact Explanations**: Provides detailed reasoning for each stock affected
- **Positive/Negative Impact Indicators**: Visual indicators for market sentiment

### User Features
- **User Accounts**: Personal accounts for saving preferences
- **Favorite Stocks**: Save and monitor specific stocks
- **Personalized Feed**: Focus on news affecting your favorite stocks

### Community Forum
- **Strategy Sharing**: Reddit-style community for sharing trading strategies
- **Discussion Threads**: Comment on posts and engage with other traders
- **Stock Tagging**: Tag relevant stocks in discussions

## Technology Stack

### Backend
- **FastAPI**: High-performance API framework
- **MongoDB**: NoSQL database for flexible data storage
- **JWT Authentication**: Secure user authentication
- **Async Architecture**: Non-blocking request handling

### Frontend
- **React**: Component-based UI library
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: Promise-based HTTP client
- **React Router**: Declarative routing

### AI Integration
- **Modular Design**: Easily swap between AI providers (OpenAI, Claude, Perplexity)
- **Placeholder Implementation**: Ready for API key integration

## Installation

### Local Development

#### Prerequisites
- Node.js (v16+)
- Python (v3.9+)
- MongoDB

#### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
# Create .env file with:
# MONGO_URL="mongodb://localhost:27017"
# DB_NAME="news_scanner_db"
# SECRET_KEY="your_secret_key"

# Start the backend server
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

#### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
yarn install

# Set environment variables
# Create .env file with:
# REACT_APP_BACKEND_URL="http://localhost:8001/api"

# Start the frontend development server
yarn start
```

### Render Deployment

This application is fully configured for deployment on Render.com with a `render.yaml` file at the root:

1. **Fork/Clone this Repository**: Make sure you have a copy in your GitHub account

2. **Sign up for Render**: Create an account at [render.com](https://render.com)

3. **Deploy the Blueprint**:
   - In your Render dashboard, click "New +"
   - Select "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` file
   - Click "Apply"

4. **Configure Environment Variables**:
   - Render will automatically set up the MongoDB database and necessary environment variables
   - For OpenAI integration, add your API key manually in the backend service environment variables:
     ```
     AI_PROVIDER=openai
     AI_API_KEY=your_openai_api_key
     ```

5. **Wait for Deployment**:
   - Render will build and deploy both the frontend and backend services
   - This usually takes a few minutes
   - Once complete, you can access your app at the provided URLs

6. **Access Your Application**:
   - Frontend: `https://stocknewsscanner-frontend.onrender.com`
   - Backend API: `https://stocknewsscanner-api.onrender.com/api`

## Usage

### Account Creation
1. Register with email, username, and password
2. Log in with your credentials
3. Start exploring news and stocks

### News Exploration
- Browse the latest news on the homepage
- Filter by category
- Click on any news item for detailed information and stock impacts

### Stock Monitoring
- Browse all stocks on the Stocks page
- Filter by exchange
- Click on a stock to see detailed information and related news
- Add stocks to favorites for quick access

### Community Engagement
- Browse forum posts on the Forum page
- Create new posts to share strategies
- Comment on existing posts
- Tag relevant stocks in your posts

## API Reference

### News Endpoints
- `GET /api/news`: List all news items
- `GET /api/news?category={category}`: Filter news by category
- `GET /api/news/{news_id}`: Get specific news item
- `GET /api/news/{news_id}/impacts`: Get stock impacts for a news item

### Stock Endpoints
- `GET /api/stocks`: List all stocks
- `GET /api/stocks?exchange={exchange}`: Filter stocks by exchange
- `GET /api/stocks/{stock_id}`: Get specific stock
- `GET /api/stocks/{stock_id}/news`: Get news affecting a specific stock

### User Endpoints
- `POST /api/users`: Create new user
- `POST /api/login`: User login
- `GET /api/users/me`: Get current user profile
- `POST /api/users/me/favorite-stocks/{stock_id}`: Add stock to favorites
- `DELETE /api/users/me/favorite-stocks/{stock_id}`: Remove stock from favorites

### Forum Endpoints
- `GET /api/forum/posts`: List all forum posts
- `POST /api/forum/posts`: Create new forum post
- `GET /api/forum/posts/{post_id}`: Get specific forum post
- `POST /api/forum/posts/{post_id}/comments`: Add comment to post
- `GET /api/forum/posts/{post_id}/comments`: Get comments for a post
- `POST /api/forum/posts/{post_id}/upvote`: Upvote a post

## AI Integration

The application is designed with placeholders for AI integration. To enable AI-powered analysis:

1. Obtain an API key from your preferred provider (OpenAI, Anthropic, Perplexity)
2. Add the key to your backend `.env` file:
   ```
   AI_PROVIDER="openai"  # or "anthropic", "perplexity"
   AI_API_KEY="your_api_key"
   ```
3. Restart the backend server

## Future Enhancements

- **Real-time News Updates**: WebSocket integration for live news feed
- **Advanced Filtering**: More granular news and stock filtering options
- **Notification System**: Alerts for news affecting favorite stocks
- **Mobile App**: Native mobile applications for iOS and Android
- **Portfolio Tracking**: Track performance of favorite stocks
- **Enhanced AI Analysis**: More detailed impact predictions with confidence levels

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Financial data is mock data for demonstration purposes
- News sources are simulated for the MVP

---

Built with ❤️ by [Your Name]
