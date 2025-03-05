#!/bin/bash
REPO_NAME = "backend-hello-service"

set -ex  # Enable debugging and stop on errors

# Logging
exec > >(tee /var/log/user-data.log) 2>&1

echo "===== Updating System Packages ====="
sudo apt update -y

echo "===== Installing Required Packages ====="
sudo apt install -y awscli docker.io

echo "===== Starting & Enabling Docker ====="
sudo systemctl start docker
sudo systemctl enable docker

echo "===== Verifying AWS CLI Installation ====="
if ! command -v aws &> /dev/null; then
    echo "AWS CLI installation failed. Exiting."
    exit 1
fi

echo "===== Configuring AWS CLI (Ensure IAM Role Attached) ====="
aws sts get-caller-identity || { echo "AWS authentication failed. Check IAM role or credentials."; exit 1; }

echo "===== Logging in to AWS ECR ====="
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 975050024946.dkr.ecr.us-east-1.amazonaws.com || {
    echo "Docker ECR login failed. Check IAM permissions."
    exit 1
}

echo "===== Checking if Repository Exists ====="
REPO_NAME="backend-hello-service"
aws ecr describe-repositories --repository-names "$REPO_NAME" --region us-east-1 || {
    echo "ECR repository $REPO_NAME not found. Exiting."
    exit 1
}

echo "===== Checking if Image Exists in Repository ====="
if ! aws ecr list-images --repository-name "$REPO_NAME" --region us-east-1 | grep -q '"imageTag": "latest"'; then
    echo "No image with tag 'latest' found in $REPO_NAME. Exiting."
    exit 1
fi

echo "===== Pulling Docker Image from ECR ====="
docker pull 975050024946.dkr.ecr.us-east-1.amazonaws.com/$REPO_NAME:latest || {
    echo "Failed to pull Docker image. Check repository name or permissions."
    exit 1
}

echo "===== Running the Docker Container ====="
docker run -d --name backend-service -p 8080:8080 975050024946.dkr.ecr.us-east-1.amazonaws.com/$REPO_NAME:latest

echo "===== Deployment Completed Successfully ====="