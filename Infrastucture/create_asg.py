import boto3

# Initialize the Auto Scaling client
autoscaling_client = boto3.client('autoscaling', region_name="us-east-1")

# Create Auto Scaling Group
response = autoscaling_client.create_auto_scaling_group(
    AutoScalingGroupName="SalWebAppASG",
    LaunchTemplate={
        'LaunchTemplateName': 'SalWebAppInstance',
        'Version': '$Latest'  # Automatically use the latest version
    },
    MinSize=1,
    MaxSize=3,
    DesiredCapacity=2,
    VPCZoneIdentifier="subnet-0927e5eb4438502b6"
)

print("✅ Auto Scaling Group Created:", response)
