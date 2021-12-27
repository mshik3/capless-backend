import json
import boto3
  

def lambda_handler(event, context):   
    # response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=S3_BUCKET_PREFIX)
    # s3_files = response["Contents"]
    # for s3_file in s3_files:
    #     file_content = s3_client.get_object(Bucket=S3_BUCKET_NAME,Key=s3_file["Key"])["Body"].read()
    #     print(file_content)
    response_list = [
        {
            'name': "Venture Standard",
            'series': "Series A",
            'industry': "Agritech",
            'capTable': "85M",
            'interested': True
        },
        {
            'name': "Sequoia Capital",
            'series': "Series B",
            'industry': "Biotech",
            'capTable': "25M",
            'interested': False
        },
        {
            'name': "Accel",
            'series': "Series C",
            'industry': "Automative",
            'capTable': "15M",
            'interested': False
        },
        {
            'name': "Kleiner Perkins",
            'series': "Series D",
            'industry': "Consulting",
            'capTable': "35M",
            'interested': True
        },
        {
            'name': "Hiya",
            'series': "Series E",
            'industry': "Social Media",
            'capTable': "45M",
            'interested': False
        },
        {
            'name': "Auth0",
            'series': "Series F",
            'industry': "CyberSecurity",
            'capTable': "35M",
            'interested': False
        },
        {
            'name': "HOVER",
            'series': "Series G",
            'industry': "Drone Tech",
            'capTable': "65M",
            'interested': False
        },
        {
            'name': "Wrench",
            'series': "Series H",
            'industry': "Manufacturing",
            'capTable': "105M",
            'interested': False
        },
        {
            'name': "Unite Us",
            'series': "Series I",
            'industry': "Human Resources",
            'capTable': "5M",
            'interested': False
        },
        {
            'name': "Shield AI",
            'series': "Series J",
            'industry': "CyberSecurity",
            'capTable': "10M",
            'interested': False
        },
    ]
    response = json.dumps(response_list)
    print(response)
    return {
        'statusCode': 200,
        'body': response
    }