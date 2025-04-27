#!/bin/bash

# Script to help with deployment to Render

# Make script executable
chmod +x deploy.sh

# Check if render-cli is installed
if ! command -v render &> /dev/null
then
    echo "render-cli is not installed. Installing..."
    npm install -g @render/cli
fi

# Login to Render (if not already logged in)
render whoami || render login

# Deploy using the render.yaml blueprint
echo "Deploying to Render..."
render blueprint apply

echo "Deployment initiated. Check the Render dashboard for progress."
echo "Visit https://dashboard.render.com to monitor your deployment."
