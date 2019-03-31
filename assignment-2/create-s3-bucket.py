import boto3

s3 = boto3.client('s3')
s3.create_bucket(Bucket='advanced-aws', CreateBucketConfiguration={'LocationConstraint': 'us-east-2'})
