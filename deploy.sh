#!/bin/bash

set -e

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m"

# Get current branch dynamically
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
DEPLOY_ENV=${DEPLOY_ENV:-"dev"}

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  SabPaisa Report API - Auto Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${YELLOW}[INFO] Branch: ${CURRENT_BRANCH}${NC}"
echo -e "${YELLOW}[INFO] Environment: ${DEPLOY_ENV}${NC}"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}[WARN] .env file not found for active environment${NC}"
fi

# Pull latest changes from current branch
echo -e "${GREEN}[INFO] Pulling latest changes from ${CURRENT_BRANCH}...${NC}"
git pull origin ${CURRENT_BRANCH}

# Build and restart Docker containers
echo -e "${GREEN}[INFO] Building Docker containers...${NC}"
docker-compose build --no-cache

echo -e "${GREEN}[INFO] Restarting containers...${NC}"
docker-compose down
docker-compose up -d

# Wait for services to be healthy
echo -e "${GREEN}[INFO] Waiting for services to start...${NC}"
sleep 15

# Run migrations
echo -e "${GREEN}[INFO] Running database migrations...${NC}"
docker-compose exec -T api python manage.py migrate --fake-initial

# Collect static files
echo -e "${GREEN}[INFO] Collecting static files...${NC}"
docker-compose exec -T api python manage.py collectstatic --noinput

# Check container status
echo -e "${GREEN}[INFO] Checking container status...${NC}"
docker-compose ps

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Deployment Completed Successfully!${NC}"
echo -e "${GREEN}========================================${NC}"

# Show logs
echo -e "${YELLOW}[INFO] Recent logs:${NC}"
docker-compose logs --tail=20 api
