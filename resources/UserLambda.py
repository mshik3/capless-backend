import json
import boto3

dynamodb = boto3.resource("dynamodb")


def lambda_handler(event, context):

    method = event["httpMethod"]

    if method == "PUT":

        print("event: " + str(event))

        str_body = event["body"]

        body = json.loads(str_body)

        if body is None:
            body = ""

        table = dynamodb.Table("UserInfo")
        response = table.put_item(
            Item={
                "user_id": body["user_id"],
                "user_email": body["user_email"],
                "firstname": body.get("firstname"),
                "lastname": body.get("lastname"),
                "company_id": body.get("company_id"),
                "startup_or_investor": body["startup_or_investor"],
            }
        )

        print(response)

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, PUT, OPTIONS",
            },
            "body": json.dumps("success"),
        }
    elif method == "GET":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, PUT, OPTIONS",
            },
            "body": json.dumps("success"),
        }
