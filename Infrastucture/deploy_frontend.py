import boto3
import os
import time

# Define the path to the credentials file inside the Infrastructure folder
credentials_file = "aws_credentials.txt"

# Read credentials
aws_credentials = {}
with open(credentials_file, "r") as file:
    for line in file:
        key, value = line.strip().split("=")
        aws_credentials[key] = value

AWS_ACCESS_KEY_ID = aws_credentials["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = aws_credentials["AWS_SECRET_ACCESS_KEY"]
AWS_DEFAULT_REGION = aws_credentials["AWS_DEFAULT_REGION"]
AWS_OUTPUT_FORMAT = aws_credentials.get("AWS_OUTPUT_FORMAT", "json")  # Default to JSON

AMI_ID = "ami-04b4f1a9cf54c11d0"
INSTANCE_TYPE = "t2.micro"
VPC_ID = "vpc-09f02049d6176fe30"
SECURITY_GROUP_ID = "sg-01f41ec5b97d3998c"
SUBNET_ID = "subnet-01874c4512136bd62"
KEY_NAME = "sal_instance_new"
ECR_REPO = "975050024946.dkr.ecr.us-east-1.amazonaws.com/frontend-service"

USER_DATA_SCRIPT = f"""#!/bin/bash
set -ex

# Logging setup
exec > >(tee /var/log/user-data.log) 2>&1

# Update system packages
sudo apt update -y && sudo apt upgrade -y

# Install required dependencies
sudo apt install -y unzip curl jq

# Install Docker
sudo apt install -y docker.io
sudo systemctl enable docker
sudo systemctl start docker

# Add ubuntu user to docker group (persistent across reboots)
sudo usermod -aG docker ubuntu

# Install AWS CLI (Latest version from AWS)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
rm -rf awscliv2.zip aws

# Verify AWS CLI installation
aws --version

# Configure AWS CLI
aws configure set aws_access_key_id {AWS_ACCESS_KEY_ID}
aws configure set aws_secret_access_key {AWS_SECRET_ACCESS_KEY}
aws configure set region {AWS_DEFAULT_REGION}
aws configure set output {AWS_OUTPUT_FORMAT}

# Authenticate with AWS ECR
aws ecr get-login-password --region {AWS_DEFAULT_REGION} | sudo docker login --username AWS --password-stdin {ECR_REPO}

# Pull the frontend image from ECR
sudo docker pull {ECR_REPO}:latest

# Run the frontend container
sudo docker run -d --name frontend-service -p 3000:3000 {ECR_REPO}:latest

# Confirm setup
sudo docker ps
echo "✅ Frontend deployment complete."
"""

# Initialize Boto3 EC2 client with credentials
session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION
)

ec2_client = session.client("ec2")

# Launch EC2 instance
response = ec2_client.run_instances(
    ImageId=AMI_ID,
    InstanceType=INSTANCE_TYPE,
    KeyName=KEY_NAME,
    MinCount=1,
    MaxCount=1,
    SecurityGroupIds=[SECURITY_GROUP_ID],
    SubnetId=SUBNET_ID,
    UserData=USER_DATA_SCRIPT,
    TagSpecifications=[{
        'ResourceType': 'instance',
        'Tags': [{'Key': 'Name', 'Value': 'Sal-Frontend-Instance'}]
    }]
)

instance_id = response["Instances"][0]["InstanceId"]
print(f"✅ Frontend EC2 instance launched: {instance_id}")

# Wait for the instance to be ready
ec2_resource = session.resource("ec2")
instance = ec2_resource.Instance(instance_id)
instance.wait_until_running()
instance.reload()

print(f"🌍 Frontend is deployed! Public IP: {instance.public_ip_address}")

# Wait for the app to start
time.sleep(60)

print("🔍 Checking if frontend is accessible...")

import requests
try:
    response = requests.get(f"http://{instance.public_ip_address}:3000", timeout=10)
    if response.status_code == 200:
        print(f"🎉 Frontend is live at: http://{instance.public_ip_address}:3000")
    else:
        print(f"⚠ Frontend returned status: {response.status_code}")
except requests.exceptions.RequestException:
    print("❌ Frontend is not accessible. Check logs on EC2 instance.")
