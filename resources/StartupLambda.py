import json
import boto3

dynamodb = boto3.resource("dynamodb")


def lambda_handler(event, context):

    method = event["httpMethod"]

    if method == "PUT":

        # print("event: " + str(event))

        # str_body = event["body"]

        # body = json.loads(str_body)

        # if body is None:
        #     body = ""

        # table = dynamodb.Table("InvestorInfo")
        # response = table.put_item(
        #     Item={
        #         "company_email": body["company_email"],
        #         "location": body["location"],
        #         "zip_code": body["zip_code"],
        #         "company_name": body["company_name"],
        #         "linkedIn_link": body["linkedIn_link"],
        #         "venture_experience": body["venture_experience"],
        #         "investment_region": body["investment_region"],
        #         "investment_check_size": body["investment_check_size"],
        #         "referral": body["referral"],
        #         "industries": body["industries"],
        #         "investment_demographic": body["investment_demographic"],
        #         "investment_description": body["investment_description"],
        #         "admins": body["admins"],
        #         "employees": body["employees"]
        #     }
        # )

        # print(response)

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
