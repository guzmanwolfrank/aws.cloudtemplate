# Use AWS config file (~/.aws/config) to load credentials!  This helps solve security risk issues.
# OR 
# Use the following scripts after header: 
# session = boto3.Session(profile_name=<...your-profile...>)
   # credentials = session.get_credentials()
   # print("AWS_ACCESS_KEY_ID = {}".format(credentials.access_key))
   # print("AWS_SECRET_ACCESS_KEY = {}".format(credentials.secret_key))
   # print("AWS_SESSION_TOKEN = {}".format(credentials.token))

import boto3

# Set up the EC2 client
ec2_client = boto3.client('ec2')

# Set up the RDS client
rds_client = boto3.client('rds')

# Set up the Elastic Load Balancer client
elb_client = boto3.client('elbv2')

# Set up the security group
response = ec2_client.create_security_group(
    Description='My security group',
    GroupName='my-security-group'
)
security_group_id = response['GroupId']

# Allow inbound traffic on port 80
ec2_client.authorize_security_group_ingress(
    GroupId=security_group_id,
    IpPermissions=[
        {
            'IpProtocol': 'tcp',
            'FromPort': 80,
            'ToPort': 80,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }
    ]
)

# Set up the EC2 instance
response = ec2_client.run_instances(
    ImageId='ami-0c55b159cbfafe1f0',
    InstanceType='t2.micro',
    MaxCount=1,
    MinCount=1,
    SecurityGroupIds=[security_group_id]
)
instance_id = response['Instances'][0]['InstanceId']

# Set up the RDS instance
response = rds_client.create_db_instance(
    DBInstanceIdentifier='my-db-instance',
    Engine='mysql',
    DBInstanceClass='db.t2.micro',
    MasterUsername='myuser',
    MasterUserPassword='mypassword'
)
db_instance_id = response['DBInstance']['DBInstanceIdentifier']

# Set up the Elastic Load Balancer
response = elb_client.create_load_balancer(
    Name='my-load-balancer',
    Subnets=['subnet-1234abcd', 'subnet-5678efgh'],
    SecurityGroups=[security_group_id]
)
load_balancer_arn = response['LoadBalancers'][0]['LoadBalancerArn']

# Create a target group
response = elb_client.create_target_group(
    Name='my-target-group',
    Protocol='HTTP',
    Port=80,
    VpcId='vpc-1234abcd'
)
target_group_arn = response['TargetGroups'][0]['TargetGroupArn']

# Register the EC2 instance with the target group
response = elb_client.register_targets(
    TargetGroupArn=target_group_arn,
    Targets=[{'Id': instance_id}]
)

# Set up the listener
response = elb_client.create_listener(
    LoadBalancerArn=load_balancer_arn,
    Protocol='HTTP',
    Port=80,
    DefaultActions=[
        {
            'Type': 'forward',
            'TargetGroupArn': target_group_arn
        }
    ]
)

# Set up autoscaling
autoscaling_client = boto3.client('autoscaling')
response = autoscaling_client.create_auto_scaling_group(
    AutoScalingGroupName='my-auto-scaling-group',
    LaunchConfigurationName='my-launch-configuration',
    MaxSize=4,
    MinSize=1
)
