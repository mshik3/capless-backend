import json
import boto3


s3 = boto3.resource("s3")
S3_BUCKET_NAME = "capless-startup-data"
FILE_NAME = "Pear_Products.json"


def lambda_handler(event, context):
    # response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=S3_BUCKET_PREFIX)
    # s3_files = response["Contents"]
    # for s3_file in s3_files:
    #     file_content = s3_client.get_object(Bucket=S3_BUCKET_NAME,Key=s3_file["Key"])["Body"].read()
    #     print(file_content)

    content_object = s3.Object(S3_BUCKET_NAME, key=FILE_NAME)
    file_content = content_object.get()["Body"].read().decode("utf-8")
    json_content = json.loads(file_content)

    print("loaded json content", json_content)

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
        },
        "body": file_content,
    }
