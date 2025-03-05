import boto3

elbv2_client = boto3.client('elbv2', region_name="us-east-1")

# Create ALB
response = elbv2_client.create_load_balancer(
    Name='SalBackendALB',
    Subnets=['subnet-0927e5eb4438502b6'],  # Update with multiple subnets for high availability
    SecurityGroups=['sg-09e22b2a8f8419c3c'],
    Scheme='internet-facing',
    Type='application',
    IpAddressType='ipv4'
)

alb_arn = response['LoadBalancers'][0]['LoadBalancerArn']
print("✅ ALB Created:", alb_arn)


target_group_response = elbv2_client.create_target_group(
    Name='SalBackendTG',
    Protocol='HTTP',
    Port=5000,  # Backend port
    VpcId='vpc-0ff5e027e4fdf7867',  # Replace with your VPC ID
    TargetType='instance',
    HealthCheckProtocol='HTTP',
    #HealthCheckPath='/health',  # Change this based on your backend
    #HealthCheckIntervalSeconds=30
)

target_group_arn = target_group_response['TargetGroups'][0]['TargetGroupArn']
print("✅ Target Group Created:", target_group_arn)
