def lambda_handler(event, context):   
    print("ScoreProcessingEngine Lambda")
    
    return {
        'statusCode': 200,
        'body': "body content"
    }