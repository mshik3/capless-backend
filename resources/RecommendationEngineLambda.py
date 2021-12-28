

def lambda_handler(event, context):   

    print("RecommendationEngineLambda")
    
    return {
        'statusCode': 200,
        'body': "RecommendationEngineLambda"
    }