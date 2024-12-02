#!/bin/bash

# Configuration
DOCKER_USERNAME="elitang"
IMAGE_NAME="youtube"
TAG="latest"
FULL_IMAGE_NAME="$DOCKER_USERNAME/$IMAGE_NAME:$TAG"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Error handling
set -e
trap 'echo -e "${RED}Error: Command failed at line $LINENO${NC}"' ERR

# Log in to Docker Hub
echo -e "${GREEN}Logging in to Docker Hub...${NC}"
docker login

# Build the Docker image
echo -e "${GREEN}Building Docker image: $FULL_IMAGE_NAME${NC}"
docker build -t $FULL_IMAGE_NAME .

# Push the image to Docker Hub
echo -e "${GREEN}Pushing image to Docker Hub...${NC}"
docker push $FULL_IMAGE_NAME

echo -e "${GREEN}Successfully built and pushed $FULL_IMAGE_NAME${NC}"