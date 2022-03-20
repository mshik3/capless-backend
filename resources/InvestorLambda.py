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

        table = dynamodb.Table("CompanyInfo")
        response = table.put_item(
            Item={
                "company_email": body["company_email"],
                "location": body.get("location"),
                "zip_code": body.get("zip_code"),
                "company_name": body.get("company_name"),
                "linkedIn_link": body.get("linkedIn_link"),
                "venture_experience": body.get("venture_experience"),
                "investment_region": body.get("investment_region"),
                "investment_check_size": body.get("investment_check_size"),
                "referral": body.get("referral"),
                "industries": body.get("industries"),
                "investment_demographic": body.get("investment_demographic"),
                "investment_description": body.get("investment_description"),
                "admins": body.get("admins"),
                "employees": body.get("employees"),
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
