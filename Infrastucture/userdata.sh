#!/bin/bash
set -ex  # Enable debugging and stop on errors

# Logging
exec > >(tee /var/log/user-data.log) 2>&1

echo "===== Updating System Packages ====="
sudo apt update -y
sudo apt install -y unzip docker.io

echo "===== Installing AWS CLI v2 ====="
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
rm -rf awscliv2.zip aws

# Ensure AWS CLI is in the PATH
export PATH=$PATH:/usr/local/bin

echo "===== Verifying AWS CLI Installation ====="
if ! command -v aws &> /dev/null; then
    echo "AWS CLI installation failed. Exiting."
    exit 1
fi

echo "===== Restarting Cloud-Init to Ensure IAM Role Availability ====="
sudo systemctl restart cloud-init

echo "===== Checking IAM Role & AWS Credentials ====="
sleep 20  # Give time for IAM role to attach
aws sts get-caller-identity || { echo "AWS authentication failed. Check IAM role or credentials."; exit 1; }

echo "===== Logging in to AWS ECR ====="
AWS_ACCOUNT_ID="975050024946"
AWS_REGION="us-east-1"
REPO_NAME="backend-hello-service"

aws ecr get-login-password --region $AWS_REGION | sudo docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com || {
    echo "Docker ECR login failed. Check IAM permissions."
    exit 1
}

echo "===== Checking if ECR Repository Exists ====="
aws ecr describe-repositories --repository-names "$REPO_NAME" --region $AWS_REGION || {
    echo "ECR repository $REPO_NAME not found. Exiting."
    exit 1
}

echo "===== Checking if Image Exists in Repository ====="
if ! aws ecr list-images --repository-name "$REPO_NAME" --region $AWS_REGION | grep -q '"imageTag": "latest"'; then
    echo "No image with tag 'latest' found in $REPO_NAME. Exiting."
    exit 1
fi

echo "===== Pulling Docker Image from ECR ====="
docker pull $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:latest || {
    echo "Failed to pull Docker image. Check repository name or permissions."
    exit 1
}

echo "===== Running the Docker Container ====="
docker run -d --name backend-service -p 8080:8080 $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:latest

echo "===== Deployment Completed Successfully ====="
