import json
import boto3

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    
    print("event: " + str(event))

    str_body = event["body"]
    
    body = json.loads(str_body)
    
    print(body)

    if body is None:
        body = ""
    
    table = dynamodb.Table('UserInfo')
    response = table.put_item(
        Item={
            'username': body["username"],
        }
    )
    
    print(response)

    return {
        'statusCode': 200,
        'body': "something"
    }