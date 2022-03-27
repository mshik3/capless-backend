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
                "username": body["username"],
                "type": body["startup_or_investor"],
                "firstname": body.get("firstname"),
                "lastname": body.get("lastname"),
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
