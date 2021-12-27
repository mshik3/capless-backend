from aws_cdk import (
    App,
    aws_apigateway as apigw,
    aws_lambda as _lambda,
    aws_s3 as _s3,
    Stack
)

class CaplessBackendStack(Stack):

    def __init__(self, scope: App, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        ########### Buckets ###########
        startup_results_bucket = _s3.Bucket(self, "capless-startup-data", bucket_name="capless-startup-data")
        raw_quality_scores_bucket = _s3.Bucket(self, "capless-raw-quality-scores", bucket_name="capless-raw-quality-scores")
        raw_match_scores_bucket = _s3.Bucket(self, "capless-raw-match-scores", bucket_name="capless-raw-match-scores")
        
        ########### Lambdas ###########
        get_feed_lambda = _lambda.Function(self,'GetFeedLambda',
            function_name='GetFeedLambda',
            handler='GetFeedLambda.lambda_handler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.from_asset('resources'),
        )

        score_processing_engine_lambda = _lambda.Function(self,'ScoreProcessingEngineLambda',
            function_name="ScoreProcessingEngineLambda",
            handler='ScoreProcessingEngineLambda.lambda_handler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.from_asset('resources'),
        )

        ########### Bucket Permissions ###########
        startup_results_bucket.grant_read(get_feed_lambda)
        startup_results_bucket.grant_write(score_processing_engine_lambda)

        raw_quality_scores_bucket.grant_read(score_processing_engine_lambda)
        raw_match_scores_bucket.grant_read(score_processing_engine_lambda)

        ########### API Gateway ###########
        api = apigw.LambdaRestApi(self, "GetFeedEndpoint", handler=get_feed_lambda, proxy=False)
        items = api.root.add_resource("feed")
        items.add_method("GET") # Gets the entire feed /feed

        item = items.add_resource("{feed_item}")
        item.add_method("GET") # Gets a companies details from the feed /feed/{company_name}