import boto3

# Initialize AWS client
ec2 = boto3.client('ec2', region_name='us-east-1')

# 1️⃣ Create a VPC
vpc_response = ec2.create_vpc(CidrBlock='10.0.0.0/16')
vpc_id = vpc_response['Vpc']['VpcId']

# Assign a name to the VPC
ec2.create_tags(Resources=[vpc_id], Tags=[{"Key": "Name", "Value": "SalCustomVPC"}])

print(f"✅ VPC Created: {vpc_id}")

# 2️⃣ Create a Subnet inside the VPC
subnet_response = ec2.create_subnet(VpcId=vpc_id, CidrBlock='10.0.1.0/24')
subnet_id = subnet_response['Subnet']['SubnetId']

# Assign a name to the Subnet
ec2.create_tags(Resources=[subnet_id], Tags=[{"Key": "Name", "Value": "SalCustomSubnet"}])

print(f"✅ Subnet Created: {subnet_id}")

# 3️⃣ Create a Security Group and allow necessary ports
sg_response = ec2.create_security_group(
    GroupName="MyCustomSG",
    Description="Security group for frontend, backend, and Jenkins",
    VpcId=vpc_id
)
sg_id = sg_response['GroupId']

# Assign a name to the Security Group
ec2.create_tags(Resources=[sg_id], Tags=[{"Key": "Name", "Value": "Sal-SecurityGroup"}])

print(f"✅ Security Group Created: {sg_id}")

# 4️⃣ Add Inbound Rules (Allow specific ports)
ports = [22, 80, 3000, 5000, 8080]  # SSH, HTTP, Frontend, Backend, Jenkins
for port in ports:
    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[{
            'IpProtocol': 'tcp',
            'FromPort': port,
            'ToPort': port,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # Allow from anywhere
        }]
    )

print(f"✅ Security Group Rules Configured: Ports {ports} Open")

print("🎉 AWS Networking Setup Complete!")
