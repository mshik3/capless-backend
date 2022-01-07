from aws_cdk import App, Stack
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_s3 as _s3
from aws_cdk import aws_apigateway as apigw

class CaplessBackendStack(Stack):

    def __init__(self, scope: App, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        ########### Buckets ###########
        startup_results_bucket = _s3.Bucket(self, "capless-startup-data", bucket_name="capless-startup-data")
        raw_quality_scores_bucket = _s3.Bucket(self, "capless-raw-quality-scores", bucket_name="capless-raw-quality-scores")
        raw_match_scores_bucket = _s3.Bucket(self, "capless-raw-match-scores", bucket_name="capless-raw-match-scores")
        recommendation_service_inputs_bucket = _s3.Bucket(self, "capless-recommendation-service-inputs", bucket_name="capless-recommendation-service-inputs")
        
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

        # ## Lambda Layer for Recommendation Engine Lambda

        # recommendation_engine_lambda_layer = _lambda.LayerVersion(self, 'recommendation-engine-lambda-layer',
        #           code = _lambda.AssetCode('resources/imports/'),
        #           compatible_runtimes = [_lambda.Runtime.PYTHON_3_7],
        # )   

        recommendation_engine_lambda = _lambda.Function(self,'RecommendationEngineLambda',
            function_name="RecommendationEngineLambda",
            handler='RecommendationEngineLambda.lambda_handler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            # layers = [recommendation_engine_lambda_layer],
            code=_lambda.Code.from_asset('resources'),
        )

        # recommendation_engine_lambda.addLayers(
        #     _lambda.LayerVersion.fromLayerVersionArn(self, 'awsNumpyLayer', 'arn:aws:lambda:ap-southeast-2:817496625479:layer:AWSLambda-Python38-SciPy1x:29')
        # )

        # recommendation_engine_lambda = _lambda.PythonFunction(self,
        #     "RecommendationEngineLambda",
        #     entry="resources",
        #     index="RecommendationEngineLambda.py",
        #     handler="lambda_handler",
        #     runtime=_lambda.Runtime.PYTHON_3_7,
        # )

        ########### Bucket Permissions ###########
        startup_results_bucket.grant_read(get_feed_lambda)
        startup_results_bucket.grant_write(score_processing_engine_lambda)

        raw_quality_scores_bucket.grant_read(score_processing_engine_lambda)
        raw_match_scores_bucket.grant_read(score_processing_engine_lambda)
        raw_quality_scores_bucket.grant_write(recommendation_engine_lambda)
        raw_match_scores_bucket.grant_write(recommendation_engine_lambda)

        recommendation_service_inputs_bucket.grant_read(recommendation_engine_lambda)

        ########### API Gateway ###########
        api = apigw.LambdaRestApi(self, "GetFeedEndpoint", handler=get_feed_lambda, proxy=False)
        items = api.root.add_resource("feed")
        items.add_method("GET") # Gets the entire feed /feed

        item = items.add_resource("{feed_item}")
        item.add_method("GET") # Gets a companies details from the feed /feed/{company_name}