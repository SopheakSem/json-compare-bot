#!/bin/bash

# JSON Compare Bot Deployment Script
set -e

echo "🚀 Starting JSON Compare Bot deployment..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.production to .env and configure your bot token:"
    echo "cp .env.production .env"
    echo "Then edit .env with your actual TELEGRAM_BOT_TOKEN"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed!"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed!"
    echo "Please install Docker Compose first: https://docs.docker.com/compose/install/"
    exit 1
fi

# Create logs directory
mkdir -p logs

# Stop existing container if running
echo "🛑 Stopping existing container..."
docker-compose down 2>/dev/null || true

# Build and start the container
echo "🏗️  Building Docker image..."
docker-compose build

echo "🚀 Starting the bot..."
docker-compose up -d

# Wait for container to be ready
echo "⏳ Waiting for container to start..."
sleep 10

# Check if container is running
if docker-compose ps | grep -q "Up"; then
    echo "✅ JSON Compare Bot is now running!"
    echo "📋 Container status:"
    docker-compose ps
    echo ""
    echo "📊 To view logs:"
    echo "docker-compose logs -f"
    echo ""
    echo "🛑 To stop the bot:"
    echo "docker-compose down"
else
    echo "❌ Failed to start the bot. Check logs:"
    docker-compose logs
    exit 1
fi
