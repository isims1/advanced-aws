# Create a new EC2 instance
ec2 = boto3.resource('ec2')
ec2.create_instances(ImageId='<ami-image-id>', MinCount=1, MaxCount=1, InstanceType=t2.micro)


# Start EC2
ec2 = boto3.client('ec2')
try:
    response = ec2.start_instances(InstanceIds=[instance_id], DryRun=False)
    print(response)
except ClientError as e:
    print(e) 

# Stop EC2
ec2 = boto3.client('ec2')
try:
    response = ec2.stop_instances(InstanceIds=[instance_id], DryRun=False)
    print(response)
except ClientError as e:
    print(e)

# Reboot EC2
ec2 = boto3.client('ec2')
try:
    response = ec2.reboot_instances(InstanceIds=['INSTANCE_ID'], DryRun=False)
    print('Success', response)
except ClientError as e:
    print('Error', e) 

# Get info about EC2
ec2 = boto3.client('ec2')
response = ec2.describe_instances()
print(response)

# Enable  and disable detailed monitoring
ec2 = boto3.client('ec2')
response = ec2.monitor_instances(InstanceIds=['INSTANCE_ID'])

ec2 = boto3.client('ec2')
response = ec2.unmonitor_instances(InstanceIds=['INSTANCE_ID']) 

# Create and delete key pairec2 = boto3.client('ec2')
ec2 = boto3.client('ec2')
response = ec2.create_key_pair(KeyName='KEY_PAIR_NAME')

ec2 = boto3.client('ec2')
response = ec2.delete_key_pair(KeyName='KEY_PAIR_NAME')

# Describe key pairs
ec2 = boto3.client('ec2')
response = ec2.describe_key_pairs()
