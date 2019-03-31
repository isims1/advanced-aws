import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Movies')

response = table.scan()

moviedata = json.dumps(response.get('Items'), indent=4, sort_keys=False, default=str)

s3 = boto3.client('s3')

rsp = s3.put_object(Body=moviedata, Bucket='advanced-aws', Key='assignment-2/movies/moviedata.json')

print(json.dumps(rsp, indent=4, sort_keys=False, default=str))
