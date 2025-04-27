# Use Node.js to build the frontend
FROM node:16-alpine as frontend-builder

# Set working directory for frontend
WORKDIR /app/frontend

# Copy frontend files
COPY frontend/package.json frontend/yarn.lock ./

# Install frontend dependencies
RUN yarn install

# Copy the rest of the frontend code
COPY frontend/ ./

# Build the frontend
RUN yarn build

# Use Python for the backend and to serve the app
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy backend files
COPY backend/ /app/backend/
COPY requirements.txt /app/

# Copy the built frontend from the frontend-builder stage
COPY --from=frontend-builder /app/frontend/build /app/frontend/build

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run the application
# Use $PORT environment variable provided by Render
CMD uvicorn backend.simple_server:app --host 0.0.0.0 --port ${PORT:-8000}
