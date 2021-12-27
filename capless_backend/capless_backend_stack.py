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

        startup_bucket = _s3.Bucket(self, "capless-startup-data", bucket_name="capless-startup-data")
        
        getFeedLambda = _lambda.Function(self,'GetFeedLambda',
            handler='GetFeedLambda.lambda_handler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.from_asset('resources'),
        )

        startup_bucket.grant_read(getFeedLambda)

        api = apigw.LambdaRestApi(self, "GetFeedEndpoint", handler=getFeedLambda, proxy=False)
        items = api.root.add_resource("feed")
        items.add_method("GET") # Gets the entire feed /feed

        item = items.add_resource("{feed_item}")
        item.add_method("GET") # Gets a companies details from the feed /feed/{company_name}