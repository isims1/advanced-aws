import sys
import boto3
import json
from botocore.exception import ClientError

ec2ID = ""
vpcID = ""
attached = False
associate = False
created_users = []

def getChoice():

    data = [['COMMAND', 'DESCRIPTION'],
        ['ec2-create', 'Create an EC2 instance.'],
        ['ec2-terminate', 'Terminate your created EC2 instance.'],
        ['ec2-stop', 'Stop your created EC2 instance.'],
        ['ec2-start', 'Start your created EC2 instance.'],
        ['ec2-status', 'Get the status of your created EC2 instance.'],
        ['ec2-reboot', 'Reboot your created EC2 instance.'],
        ['ec2-monitor', 'Monitor your created EC2 instance.'],
        ['ec2-unmonitor', 'Unmonitor your created EC2 instance.'],
        ['vpc-create', 'Create a custom VPC and allocate and elastic IP.'],
        ['vpc-attach', 'Attach an internet gateway to your VPC.'],
        ['vpc-detach', 'Detach the internet gateway from your VPC.'],
        ['vpc-delete', 'Delete your custom VPC.'],
        ['ip-associate', 'Associate your IP address to your EC2 instance.'],
        ['ip-disassociate', 'Disassociate your IP address from you EC2 instance.'],
        ['iam-create-user', 'Create a new user.'],
        ['iam-attach-policy', 'Attach EC2 policy to a user.'],
        ['quit', 'Release all resources and exit.']]

    dash = '-' * 70
    for i in range(len(data)):
        if i == 0:
            print(dash)
            print('{:<25s}{:<40s}'.format(data[i][0],data[i][1]))
            print(dash)
        else:
            print('{:<25s}{:<40s}'.format(data[i][0],data[i][1]))
    print(dash)
    choose = input(">>> ")
    choice = choose.lower()

    return choice

def ec2Create():
    try:
        ec2 = boto3.resource('ec2')
        response = ec2.create_instances(ImageId='ami-0f65671a86f061fcd', MinCount=1, MaxCount=1, InstanceType='t2.micro')
        return response
    except ClientError as e:
        return e.response

def ec2Terminate(ec2ID):
    try:
        ec2 = boto3.resource('ec2')
        response = ec2.instances.filter(InstanceIds=[ec2ID]).terminate()
        return response
    except ClientError as e:
        return e.response

def ec2Start(ec2ID):
    try:
        ec2 = boto3.resource('ec2')
        response = ec2.instances.filter(InstanceIds=[ec2ID]).start()
        return response
    except ClientError as e:
        return e.response

def ec2Stop(ec2ID):
    try:
        ec2 = boto3.resource('ec2')
        response = ec2.instances.filter(InstanceIds=[ec2ID]).stop()
        return response
    except ClientError as e:
        return e.response

def ec2Status(ec2ID):
    try:
        ec2 = boto3.resource('ec2')
        instance = ec2.Instance(ec2ID)
        response = instance.state['Name']
        return response
    except ClientError as e:
        return e.response

def ec2Reboot(ec2ID):
    try:
        ec2 = boto3.client('ec2')
        response = ec2.reboot_instances(InstanceIds=[ec2ID], DryRun=False)
        return response
    except ClientError as e:
        return e.response

def ec2Monitor(ec2ID):
    try:
        ec2 = boto3.client('ec2')
        response = ec2.monitor_instances(InstanceIds=[ec2ID], DryRun=False)
        return response
    except ClientError as e:
        return e.response

def ec2Unmonitor(ec2ID):
    try:
        ec2 = boto3.client('ec2')
        response = ec2.unmonitor_instances(InstanceIds=[ec2ID], DryRun=False)
        return response
    except ClientError as e:
        return e.response

def vpcCreate():
    try:
        ec2 = boto3.client('ec2')

        vpc_response = ec2.create_vpc(CidrBlock='10.0.0.0/24')
        vpcID = vpc_response.get('Vpc', {}).get('VpcId')

        subnet_response = ec2.create_subnet(CidrBlock='10.0.0.0/25',VpcId=vpcID)
        subnetID = subnet_response.get('Subnet', {}).get('SubnetId')

        gateway_response = ec2.create_internet_gateway()
        gatewayID = gateway_response.get('InternetGateway', {}).get('InternetGatewayId')

        ip_response = ec2.allocate_address(Domain='vpc')
        allocationID = ip_response.get("AllocationId", {})

        response = {"create_vpc": vpc_response, "create_subnet": subnet_response, "create_gateway": gateway_response, "allocate_ip": ip_response}
        return response

    except ClientError as e:
        return e.response

def vpcAttach(vpcID, gatewayID):
    try:
        ec2 = boto3.resource('ec2')
        gateway = ec2.InternetGateway(gatewayID)
        response = gateway.attach_to_vpc(VpcId=vpcID)
        return response

    except ClientError as e:
        return e.response

def vpcDetach(vpcID, gatewayID):
    try:
        ec2 = boto3.resource('ec2')
        gateway = ec2.InternetGateway(gatewayID)
        response = gateway.detach_from_vpc(VpcId=vpcID)
        return response

    except ClientError as e:
        return e.response

def vpcDelete(vpcID, gatewayID, allocationID, attached):
    try:
        ec2 = boto3.resource('ec2')
        ec2client = ec2.meta.client
        vpc = ec2.Vpc(vpcID)

        for subnet in vpc.subnets.all():
            subnet.delete()

        if attached:
            vpc.detach_internet_gateway(InternetGatewayId = gatewayID)
        gw = ec2.InternetGateway(gatewayID)
        gw.delete()

        e = boto3.client('ec2')
        alloc = e.release_address(AllocationId=allocationID)

        response = ec2client.delete_vpc(VpcId = vpcID)
        return response

    except ClientError as e:
        return e.response

def ipAssociate(ec2ID, allocationID):
    try:
        ec2 = boto3.resource('ec2')
        address = ec2.VpcAddress(allocationID)
        response = address.associate(InstanceId=ec2ID)

        return response

    except ClientError as e:
        return e.response

def ipDisassociate(allocationID):
    try:
        ec2 = boto3.resource('ec2')
        address = ec2.VpcAddress(allocationID)
        response = address.association.delete()

        return response

    except ClientError as e:
        return e.response

def iamCreateUser(user_name):
    try:
        iam = boto3.client('iam')
        user_response = iam.create_user(UserName=user_name)

        key_response = iam.create_access_key(UserName=user_name)

        response = {"User": user_response, "Key": key_response}

        return response

    except ClientError as e:
        return e.response

choice = getChoice()

while choice!="quit":
    if choice=="ec2-create":
        if ec2ID == "":
            response = ec2Create()
            print(response)
            ec2ID = response[0].instance_id
        else:
            print("You have already created an EC2 instance, the EC2 ID is:" + ec2ID)
    elif choice=="ec2-terminate":
        if ec2ID == "":
            print("You haven't created an EC2 instance to terminate.")
        else:
            response = ec2Terminate(ec2ID)
            ec2ID = ""
            print(json.dumps(response, indent=4, sort_keys=False))
    elif choice=="ec2-stop":
        if ec2ID == "":
            print("You haven't created an EC2 instance to stop.")
        else:
            response = ec2Stop(ec2ID)
            print(json.dumps(response, indent=4, sort_keys=False))
    elif choice=="ec2-start":
        if ec2ID == "":
            print("You haven't created an EC2 instance to start.")
        else:
            response = ec2Start(ec2ID)
            print(json.dumps(response, indent=4, sort_keys=False))
    elif choice=="ec2-status":
        if ec2ID == "":
            print("You haven't created an EC2 instance to check the status of.")
        else:
            response = ec2Status(ec2ID)
            print(json.dumps(response, indent=4, sort_keys=False))
    elif choice=="ec2-reboot":
        if ec2ID == "":
            print("You haven't created an EC2 instance to reboot.")
        else:
            response = ec2Reboot(ec2ID)
            print(json.dumps(response, indent=4, sort_keys=False))
    elif choice=="ec2-monitor":
        if ec2ID == "":
            print("You haven't created an EC2 instance to unmonitor.")
        else:
            response = ec2Monitor(ec2ID)
            print(json.dumps(response, indent=4, sort_keys=False))
    elif choice=="ec2-unmonitor":
        if ec2ID == "":
            print("You haven't created an EC2 instance to unmonitor.")
        else:
            response = ec2Unmonitor(ec2ID)
            print(json.dumps(response, indent=4, sort_keys=False))
    elif choice=="vpc-create":
        if vpcID == "":
            response = vpcCreate()

            print(json.dumps(response, indent=4, sort_keys=False))

            vpcID = response.get('create_vpc', {}).get('Vpc').get('VpcId')
            subnetID = response.get("create_subnet", {}).get("Subnet").get("SubnetId")
            gatewayID = response.get("create_gateway", {}).get("InternetGateway").get("InternetGatewayId")
            allocationID = response.get("allocate_ip", {}).get("AllocationId")

        else:
            print("You have already created a VPC.")
    elif choice=="vpc-attach":
        if vpcID != "":
            response = vpcAttach(vpcID, gatewayID)
            print(json.dumps(response, indent=4, sort_keys=False))
            attached = True
        else:
            print("You haven't created a VPC.")
    elif choice=="vpc-detach":
        if vpcID != "":
            response = vpcDetach(vpcID, gatewayID)
            print(json.dumps(response, indent=4, sort_keys=False))
            attached = False
        else:
            print("You haven't created a VPC.")
    elif choice=="vpc-delete":
        if vpcID != "":
            response = vpcDelete(vpcID, gatewayID, allocationID, attached)
            print(json.dumps(response, indent=4, sort_keys=False))
            vpcID = ""
        else:
            print("You haven't created a VPC.")
    elif choice=="ip-associate":
        if vpcID != "":
            if ec2ID != "":
                if associate == False:
                    response = ipAssociate(ec2ID, allocationID)
                    associate = True
                    print(json.dumps(response, indent=4, sort_keys=False))
                else:
                    print("You already associated your IP address.")
            else:
                print("You haven't create an EC2 instance.")
        else:
            print("You haven't created a VPC.")
    elif choice=="ip-disassociate":
        if associate:
            response = ipDisassociate(allocationID)
            print(json.dumps(response, indent=4, sort_keys=False))
            associate = False
        else:
            print("You haven't associated your IP address.")
    elif choice=="iam-create-user":
        print("Enter the user's name.")
        nm_inpt = input(">>> ")

        response = iamCreateUser(nm_inpt)
        print(json.dumps(response, indent=4, sort_keys=False, default=str))
        created_users.append(nm_inpt)
    else:
        print("Invalid entry, please choose again")
        print("\n")

    choice = getChoice()

if choice=="quit":
    if ec2ID != "":
        ec2Terminate(ec2ID)
    if vpcID != "":
        vpcDelete(vpcID, gatewayID, allocationID, attached)
    if not created_users:
        response = "No created users"
    else:
        iam = boto3.client('iam')
        for nm in created_users:
            paginator = iam.get_paginator('list_access_keys')
            for response in paginator.paginate(UserName=nm):
                accessKeyID = response.get('AccessKeyMetadata', {})[0].get('AccessKeyId')

            iam.delete_access_key(AccessKeyId=accessKeyID, UserName=nm)
            iam.delete_user(UserName=nm)
    print("All resources were released."
)
