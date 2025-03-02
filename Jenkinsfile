#!/bin/bash
set -e  # Exit on error
set -o pipefail  # Fail if any command fails in a pipeline

# AWS Configuration
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Define ECR Repositories
ECR_REPO_BACKEND="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/backend-hello-service"
ECR_REPO_FRONTEND="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/frontend-service"

# Ensure AWS CLI is configured
aws configure list || { echo "❌ AWS CLI is not configured! Exiting..."; exit 1; }

# Login to AWS ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build & Push Backend
cd backend/helloService
docker build --platform linux/amd64 -t backend-hello-service .
docker tag backend-hello-service:latest $ECR_REPO_BACKEND:latest
docker push $ECR_REPO_BACKEND:latest
cd ../..

# Build & Push Frontend
cd frontend
docker build --platform linux/amd64 -t frontend-service .
docker tag frontend-service:latest $ECR_REPO_FRONTEND:latest
docker push $ECR_REPO_FRONTEND:latest

echo "✅ All Docker images have been built and pushed successfully!"