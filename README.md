# Connect The Plots Scanner

A financial dashboard application that displays stock market news and performance data for stocks, mutual funds, and ETFs.

## Features

- Real-time financial data display with automatic rotation between stocks, mutual funds, and ETFs every 20 seconds
- Latest business news from NewsAPI
- Dark theme UI with responsive design
- Countdown timer showing time until next data rotation
- Manual selection between different financial instrument types
- Displays 10 instruments for each category

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React with Tailwind CSS
- **Data Sources**: NewsAPI for business news, mock data for financial instruments

## Local Development

### Prerequisites

- Python 3.9+
- Node.js 16+
- Yarn

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your NewsAPI key:
   ```
   NEWS_API_KEY=your_api_key_here
   ```

5. Run the server:
   ```
   uvicorn simple_server:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   yarn install
   ```

3. Create a `.env` file:
   ```
   REACT_APP_BACKEND_URL=http://localhost:8000
   ```

4. Start the development server:
   ```
   yarn start
   ```

## Deployment to Render

This project is configured for easy deployment to Render using the included `render.yaml` blueprint.

### Deployment Steps

#### Option 1: Using the Render Dashboard (Recommended)

1. Fork or clone this repository to your GitHub account.

2. Sign up for a [Render account](https://render.com/) if you don't have one.

3. In the Render dashboard, click on "New" and select "Blueprint".

4. Connect your GitHub account and select the repository.

5. Render will automatically detect the `render.yaml` file and create the necessary services:
   - Backend API service (Docker)
   - Frontend web service (Node.js)

6. Add your NewsAPI key as an environment variable for the backend service:
   - Go to the backend service in the Render dashboard
   - Navigate to the "Environment" tab
   - Add a new environment variable:
     - Key: `NEWS_API_KEY`
     - Value: Your NewsAPI key
   - Save changes and deploy

7. Wait for both services to deploy. The frontend will automatically be configured to connect to the backend.

#### Option 2: Using the Deployment Script

1. Make sure the deployment script is executable:
   ```
   chmod +x deploy.sh
   ```

2. Run the deployment script:
   ```
   ./deploy.sh
   ```

3. Follow the prompts to log in to Render if needed.

4. The script will deploy the application using the `render.yaml` blueprint.

5. After deployment, add your NewsAPI key as an environment variable in the Render dashboard.

### Important Notes for Render Deployment

1. The backend service uses Docker and will automatically use the Dockerfile in the repository.

2. The frontend service is configured to use the backend service's host, with HTTPS protocol.

3. Both services are set to auto-deploy when changes are pushed to the repository.

4. The health check endpoint at `/health` is used to monitor the backend service.

### Environment Variables

- **Backend**:
  - `NEWS_API_KEY`: Your NewsAPI key

- **Frontend**:
  - `REACT_APP_BACKEND_URL`: Automatically set by Render to point to the backend service

## Project Structure

- `/backend`: FastAPI server code
  - `simple_server.py`: Main server file with API endpoints
  - `requirements.txt`: Python dependencies

- `/frontend`: React application
  - `/src`: Source code
    - `/components`: React components
    - `App.js`: Main application component
  - `package.json`: Node.js dependencies

- `Dockerfile`: Docker configuration for the backend
- `render.yaml`: Render deployment configuration
