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

# Set compose file based on environment
COMPOSE_FILE="docker-compose.yml"
if [ -f "docker-compose.${DEPLOY_ENV}.yml" ]; then
    COMPOSE_FILE="docker-compose.yml -f docker-compose.${DEPLOY_ENV}.yml"
    echo -e "${GREEN}[INFO] Using environment-specific compose: docker-compose.${DEPLOY_ENV}.yml${NC}"
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  SabPaisa Report API - Auto Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${YELLOW}[INFO] Branch: ${CURRENT_BRANCH}${NC}"
echo -e "${YELLOW}[INFO] Environment: ${DEPLOY_ENV}${NC}"

# Check if environment file exists
if [ ! -f ".env.${DEPLOY_ENV}" ]; then
    echo -e "${RED}[ERROR] .env.${DEPLOY_ENV} file not found!${NC}"
    exit 1
fi

# Pull latest changes from current branch
echo -e "${GREEN}[INFO] Pulling latest changes from ${CURRENT_BRANCH}...${NC}"
git pull origin ${CURRENT_BRANCH}

echo -e "${GREEN}[INFO] Using environment file: .env.${DEPLOY_ENV}${NC}"
echo -e "${YELLOW}[INFO] ALLOWED_HOSTS: $(grep ALLOWED_HOSTS .env.${DEPLOY_ENV})${NC}"

# Build and restart Docker containers
echo -e "${GREEN}[INFO] Building Docker containers...${NC}"
docker compose -f ${COMPOSE_FILE} build --no-cache

echo -e "${GREEN}[INFO] Restarting containers...${NC}"
docker compose -f ${COMPOSE_FILE} down
docker compose -f ${COMPOSE_FILE} up -d

# Wait for services to be healthy
echo -e "${GREEN}[INFO] Waiting for services to start...${NC}"
sleep 15

# Run migrations
echo -e "${GREEN}[INFO] Running database migrations...${NC}"
docker compose -f ${COMPOSE_FILE} exec -T api python manage.py migrate --fake-initial

# Collect static files
echo -e "${GREEN}[INFO] Collecting static files...${NC}"
docker compose -f ${COMPOSE_FILE} exec -T api python manage.py collectstatic --noinput

# Check container status
echo -e "${GREEN}[INFO] Checking container status...${NC}"
docker compose -f ${COMPOSE_FILE} ps

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Deployment Completed Successfully!${NC}"
echo -e "${GREEN}========================================${NC}"

# Show logs
echo -e "${YELLOW}[INFO] Recent logs:${NC}"
docker compose -f ${COMPOSE_FILE} logs --tail=20 api
