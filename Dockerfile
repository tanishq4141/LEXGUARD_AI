# Stage 1: Build the React Frontend
FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend
# Copy package files
COPY frontend/package*.json ./
# Install dependencies
RUN npm ci

# Copy frontend source code
COPY frontend/ .
# Build the frontend for production
RUN npm run build


# Stage 2: Build the FastAPI Backend & Serve
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies required for python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the backend source code
COPY backend/ backend/

# Copy the compiled frontend static files from Stage 1 into the backend folder
# The backend/main.py is configured to serve from ../frontend/dist
COPY --from=frontend-build /app/frontend/dist /app/frontend/dist

# Set environment variables for Cloud Run
ENV PORT=8080
ENV HOST=0.0.0.0

# Expose the port
EXPOSE 8080

# Start the FastAPI server using Uvicorn
WORKDIR /app/backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
