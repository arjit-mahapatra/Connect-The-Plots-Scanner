# Deploying Connect-The-Plots-Scanner as a Web Service on Render

This guide provides step-by-step instructions for deploying the application as a single web service on Render.

## Prerequisites

1. A [Render account](https://render.com/signup)
2. Your NewsAPI key
3. Your project code pushed to a GitHub repository

## Deployment Steps

### Option 1: Using the Render Dashboard (Recommended)

1. **Log in to Render**
   - Go to [dashboard.render.com](https://dashboard.render.com/) and log in to your account

2. **Create a New Web Service**
   - Click the "New +" button in the top right corner
   - Select "Web Service" from the dropdown menu

3. **Connect Your Repository**
   - Choose "GitHub" as your deployment method
   - Connect your GitHub account if you haven't already
   - Select the repository containing your Connect-The-Plots-Scanner code

4. **Configure the Web Service**
   - **Name**: Enter a name for your service (e.g., "connect-the-plots")
   - **Region**: Choose the region closest to your users
   - **Branch**: Select the branch you want to deploy (usually "main" or "master")
   - **Runtime**: Select "Docker"
   - **Instance Type**: Choose the "Free" plan for testing or a paid plan for production
   - **Health Check Path**: Enter "/health"

5. **Set Environment Variables**
   - Scroll down to the "Environment" section
   - Click "Add Environment Variable"
   - Add the following variables:
     - Key: `NEWS_API_KEY`, Value: Your NewsAPI key
     - Key: `PORT`, Value: `8000`
     - Key: `REACT_APP_BACKEND_URL`, Value: Leave empty (since frontend and backend are on the same origin)

6. **Deploy the Service**
   - Click "Create Web Service"
   - Render will start building and deploying your application
   - This process may take a few minutes

7. **Access Your Application**
   - Once deployment is complete, Render will provide a URL for your application
   - Click on the URL to access your deployed application

### Option 2: Using the Render Blueprint

1. **Prepare Your Repository**
   - Make sure your repository contains the updated `render.yaml` file
   - Push your changes to GitHub

2. **Log in to Render**
   - Go to [dashboard.render.com](https://dashboard.render.com/) and log in to your account

3. **Create a New Blueprint**
   - Click the "New +" button in the top right corner
   - Select "Blueprint" from the dropdown menu
   - Connect your GitHub account if you haven't already
   - Select the repository containing your Connect-The-Plots-Scanner code

4. **Apply the Blueprint**
   - Render will detect the `render.yaml` file and show the services to be created
   - Click "Apply Blueprint"
   - Render will create the web service defined in your `render.yaml` file

5. **Set Environment Variables**
   - After the service is created, click on it to go to its dashboard
   - Navigate to the "Environment" tab
   - Add your NewsAPI key:
     - Key: `NEWS_API_KEY`, Value: Your NewsAPI key
   - Click "Save Changes"

6. **Deploy the Service**
   - Click "Manual Deploy" and select "Deploy latest commit"
   - Wait for the deployment to complete

7. **Access Your Application**
   - Once deployment is complete, click on the URL provided by Render to access your application

### Option 3: Using the Command Line

1. **Install the Render CLI**
   ```bash
   npm install -g @render/cli
   ```

2. **Log in to Render**
   ```bash
   render login
   ```

3. **Deploy Using the Blueprint**
   ```bash
   render blueprint apply
   ```

4. **Set Environment Variables**
   - After deployment, go to the Render dashboard
   - Click on your web service
   - Navigate to the "Environment" tab
   - Add your NewsAPI key
   - Click "Save Changes" and redeploy

## Troubleshooting

### Build Fails

- Check the build logs for specific errors
- Ensure your Dockerfile is correctly configured
- Verify that all dependencies are properly specified

### Application Not Loading

- Check if the health check endpoint is responding correctly
- Verify that the frontend build process completed successfully
- Check the logs for any runtime errors

### API Requests Failing

- Ensure your NewsAPI key is correctly set in the environment variables
- Check the logs for any API-related errors
- Verify that the frontend is making requests to the correct endpoints

## Monitoring and Maintenance

- Use the Render dashboard to monitor your service's performance
- Check logs regularly for any issues
- Set up alerts for service outages or high resource usage

## Updating Your Application

1. Push changes to your GitHub repository
2. If auto-deploy is enabled, Render will automatically deploy the changes
3. Otherwise, manually deploy from the Render dashboard
