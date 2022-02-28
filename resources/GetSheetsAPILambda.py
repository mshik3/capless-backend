import json
import boto3


s3 = boto3.resource("s3")
S3_BUCKET_NAME = 'capless-app-data'
FILE_NAME = 'google_sheets_api.json'

def lambda_handler(event, context):
    content_object = s3.Object(S3_BUCKET_NAME, key=FILE_NAME)
    file_content = content_object.get()['Body'].read().decode('utf-8')

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET'
        },
        'body': file_content
    }