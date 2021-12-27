from aws_cdk import (
    App,
    aws_apigateway as apigw,
    aws_lambda as _lambda,
    Stack
)

class CaplessBackendStack(Stack):

    def __init__(self, scope: App, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        getFeedLambda = _lambda.Function(self,'GetFeedLambda',
            handler='GetFeedLambda.lambda_handler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.from_asset('resources'),
        )

        api = apigw.LambdaRestApi(self, "GetFeedEndpoint", handler=getFeedLambda)