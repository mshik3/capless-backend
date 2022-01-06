import boto3
from pandas import pandas as pd

s3 = boto3.client("s3")

def calculate_quality_scores(startup_attributes_list):
    total_scores_dict = {}
    for startup_attributes in startup_attributes_list:
        company_name = startup_attributes["company_name"]
        total_scores_dict[company_name] = 0
        for key in startup_attributes.keys():
            if startup_attributes[key] != "None":
                total_scores_dict[company_name] += 1
    
    return total_scores_dict

def lambda_handler(event, context):   
    
    # Quality score calculation
    startup_attributes = s3.get_object(Bucket="recommendation_service_inputs", Key="startups/attributes/2021-12-28.csv")
    investors_attributes = s3.get_object(Bucket="recommendation_service_inputs", Key="investors/attributes/2021-12-28.csv")
    
    startup_attributes_df = pd.read_csv(startup_attributes.get("Body"))
    
    startup_attributes_list = startup_attributes_df.to_dict("records")
    
    print(startup_attributes_dict)
    
    quality_scores = calculate_quality_scores(startup_attributes_list)

    print(quality_scores)
    # Match score calculation

    startup_preference_ranks =startup_attributes = s3.get_object(Bucket="recommendation_service_inputs", Key="startups/preferences/2021-12-28_rank.csv")
    startup_preference_values =startup_attributes = s3.get_object(Bucket="recommendation_service_inputs", Key="startups/preferences/2021-12-28_values.csv")

    return {
        'statusCode': 200,
        'body': {
            "startup_attributes_dict": startup_attributes_dict,
            "total_scores_dict": quality_scores
        }
    }