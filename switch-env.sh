#!/bin/bash

# ===============================================
# Environment Switcher Script
# Switches between different environment configurations
# ===============================================

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
    echo -e "${YELLOW}Usage: $0 <environment>${NC}"
    echo ""
    echo "Available environments:"
    echo "  local  - Local development environment"
    echo "  dev    - Development server environment (13.127.244.103)"
    echo "  stage  - Staging environment"
    echo "  prod   - Production environment (13.201.46.165)"
    echo ""
    echo "Example: $0 dev"
    exit 1
}

# Check if environment argument is provided
if [ $# -eq 0 ]; then
    usage
fi

ENV=$1

# Validate environment
if [ "$ENV" != "local" ] && [ "$ENV" != "dev" ] && [ "$ENV" != "stage" ] && [ "$ENV" != "prod" ]; then
    echo -e "${RED}Error: Invalid environment '$ENV'${NC}"
    usage
fi

echo -e "${GREEN}Switching to $ENV environment...${NC}"

# Backend environment
BACKEND_DIR="./sabpaisa-report-api"
if [ -f "$BACKEND_DIR/.env.$ENV" ]; then
    cp "$BACKEND_DIR/.env.$ENV" "$BACKEND_DIR/.env"
    echo -e "${GREEN}✓ Backend environment set to $ENV${NC}"
else
    echo -e "${RED}✗ Backend .env.$ENV not found${NC}"
fi

# Frontend environment
FRONTEND_DIR="./sabpaisa-report-ui"
if [ -f "$FRONTEND_DIR/.env.$ENV" ]; then
    cp "$FRONTEND_DIR/.env.$ENV" "$FRONTEND_DIR/.env"
    echo -e "${GREEN}✓ Frontend environment set to $ENV${NC}"
else
    echo -e "${RED}✗ Frontend .env.$ENV not found${NC}"
fi

echo ""
echo -e "${GREEN}Environment switched to: $ENV${NC}"
echo -e "${YELLOW}Note: Restart your services for changes to take effect${NC}"
