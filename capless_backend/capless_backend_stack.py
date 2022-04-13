from aws_cdk import App, Stack
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_s3 as _s3
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_lambda_python_alpha as lambda_python
from aws_cdk import aws_dynamodb as dynamo

LAMBDA_HANDLER_NAME = "lambda_handler"
LAMBDA_CODE_FOLDER = "resources"


class CaplessBackendStack(Stack):
    def __init__(self, scope: App, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        ########### Buckets ###########
        company_profiles_bucket = _s3.Bucket(
            self, "capless-company-profiles", bucket_name="capless-company-profiles"
        )
        user_profiles_bucket = _s3.Bucket(
            self, "capless-user-profiles", bucket_name="capless-user-profiles"
        )
        startup_results_bucket = _s3.Bucket(
            self, "capless-startup-data", bucket_name="capless-startup-data"
        )
        capless_app_data_bucket = _s3.Bucket(
            self, "capless-app-data", bucket_name="capless-app-data"
        )
        raw_quality_scores_bucket = _s3.Bucket(
            self, "capless-raw-quality-scores", bucket_name="capless-raw-quality-scores"
        )
        raw_match_scores_bucket = _s3.Bucket(
            self, "capless-raw-match-scores", bucket_name="capless-raw-match-scores"
        )
        recommendation_service_inputs_bucket = _s3.Bucket(
            self,
            "capless-recommendation-service-inputs",
            bucket_name="capless-recommendation-service-inputs",
        )

        ########### Lambdas ###########
        get_feed_lambda = self.create_lambda("GetFeedLambda")

        sheets_api_lambda = self.create_lambda("GetSheetsAPILambda")

        score_processing_engine_lambda = self.create_lambda(
            "ScoreProcessingEngineLambda", layers=True
        )

        recommendation_engine_lambda = self.create_lambda(
            "RecommendationEngineLambda", layers=True
        )

        user_lambda = self.create_lambda("UserLambda", layers=True)

        investor_lambda = self.create_lambda("InvestorLambda", layers=True)
        
        startup_lambda = self.create_lambda("StartupLambda", layers=True)

        ########### Bucket Permissions ###########
        startup_results_bucket.grant_read(get_feed_lambda)
        startup_results_bucket.grant_write(score_processing_engine_lambda)
        capless_app_data_bucket.grant_read(sheets_api_lambda)

        raw_quality_scores_bucket.grant_read(score_processing_engine_lambda)
        raw_match_scores_bucket.grant_read(score_processing_engine_lambda)
        raw_quality_scores_bucket.grant_write(recommendation_engine_lambda)
        raw_match_scores_bucket.grant_write(recommendation_engine_lambda)

        recommendation_service_inputs_bucket.grant_read(recommendation_engine_lambda)

        company_profiles_bucket.grant_read_write(investor_lambda)
        company_profiles_bucket.grant_read_write(startup_lambda)
        user_profiles_bucket.grant_read_write(user_lambda)

        ########### DynamoDB ###########

        user_table = dynamo.Table(
            self,
            "UserInfo",
            table_name="UserInfo",
            partition_key=dynamo.Attribute(
                name="user_id", type=dynamo.AttributeType.STRING
            ),
        )

        company_table = dynamo.Table(
            self,
            "CompanyInfo",
            table_name="CompanyInfo",
            partition_key=dynamo.Attribute(
                name="company_email", type=dynamo.AttributeType.STRING
            ),
        )

        investor_table = dynamo.Table(
            self,
            "InvestorInfo",
            table_name="InvestorInfo",
            partition_key=dynamo.Attribute(
                name="company_id", type=dynamo.AttributeType.STRING
            ),
        )

        startup_table = dynamo.Table(
            self,
            "StartupInfo",
            table_name="StartupInfo",
            partition_key=dynamo.Attribute(
                name="company_id", type=dynamo.AttributeType.STRING
            ),
        )

        ########### DynamoDB Permissions ###########

        user_table.grant_read_write_data(user_lambda)
        user_table.grant_write_data(investor_lambda)

        company_table.grant_read_write_data(investor_lambda)
        company_table.grant_read_write_data(startup_lambda)

        investor_table.grant_read_write_data(investor_lambda)
        startup_table.grant_read_write_data(startup_lambda)

        ########### API Gateway ###########
        get_feed_api = apigw.LambdaRestApi(
            self, "GetFeedEndpoint", handler=get_feed_lambda, proxy=False
        )
        items = get_feed_api.root.add_resource("feed")
        items.add_method("GET")  # Gets the entire feed /feed

        item = items.add_resource("{feed_item}")
        item.add_method(
            "GET"
        )  # Gets a companies details from the feed /feed/{company_name}

        sheets_api = apigw.LambdaRestApi(
            self, "SheetsAPIEndpoint", handler=sheets_api_lambda, proxy=False
        )
        sheets = sheets_api.root.add_resource("sheets")
        sheets.add_method("GET")  # Creating a new user

        user_api = apigw.LambdaRestApi(
            self,
            "UserEndpoint",
            rest_api_name="UserEndpoint",
            handler=user_lambda,
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
                allow_headers=["*"],
            ),
        )
        user = user_api.root.add_resource("user")
        user.add_method(
            "PUT",
            method_responses=[
                apigw.MethodResponse(
                    # Successful response from the integration
                    status_code="200",
                    # Define what parameters are allowed or not
                    response_parameters={
                        "method.response.header._content-_type": True,
                        "method.response.header._access-_control-_allow-_origin": True,
                    },
                ),
                apigw.MethodResponse(
                    # Same thing for the error responses
                    status_code="400",
                    response_parameters={
                        "method.response.header._content-_type": True,
                        "method.response.header._access-_control-_allow-_origin": True,
                    },
                ),
            ],
        )  # Creating/Updating a user
        user.add_method("GET", method_responses=[
                apigw.MethodResponse(
                    # Successful response from the integration
                    status_code="200",
                    # Define what parameters are allowed or not
                    response_parameters={
                        "method.response.header._content-_type": True,
                        "method.response.header._access-_control-_allow-_origin": True,
                    },
                ),
                apigw.MethodResponse(
                    # Same thing for the error responses
                    status_code="400",
                    response_parameters={
                        "method.response.header._content-_type": True,
                        "method.response.header._access-_control-_allow-_origin": True,
                    },
                ),
            ],)  # Get a User
        
        investor_api = apigw.LambdaRestApi(
            self,
            "InvestorEndpoint",
            rest_api_name="InvestorEndpoint",
            handler=investor_lambda,
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
                allow_headers=["*"],
            ),
        )
        investor = investor_api.root.add_resource("investor")
        investor.add_method(
            "PUT",
            method_responses=[
                apigw.MethodResponse(
                    # Successful response from the integration
                    status_code="200",
                    # Define what parameters are allowed or not
                    response_parameters={
                        "method.response.header._content-_type": True,
                        "method.response.header._access-_control-_allow-_origin": True,
                    },
                ),
                apigw.MethodResponse(
                    # Same thing for the error responses
                    status_code="400",
                    response_parameters={
                        "method.response.header._content-_type": True,
                        "method.response.header._access-_control-_allow-_origin": True,
                    },
                ),
            ],
        )  # Creating/Updating a investor
        investor.add_method("GET", method_responses=[
                apigw.MethodResponse(
                    # Successful response from the integration
                    status_code="200",
                    # Define what parameters are allowed or not
                    response_parameters={
                        "method.response.header._content-_type": True,
                        "method.response.header._access-_control-_allow-_origin": True,
                    },
                ),
                apigw.MethodResponse(
                    # Same thing for the error responses
                    status_code="400",
                    response_parameters={
                        "method.response.header._content-_type": True,
                        "method.response.header._access-_control-_allow-_origin": True,
                    },
                ),
            ],)  # Get a investor

        startup_api = apigw.LambdaRestApi(
            self,
            "StartupEndpoint",
            rest_api_name="StartupEndpoint",
            handler=startup_lambda,
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
                allow_headers=["*"],
            ),
        )
        startup = startup_api.root.add_resource("startup")
        startup.add_method(
            "PUT",
            method_responses=[
                apigw.MethodResponse(
                    # Successful response from the integration
                    status_code="200",
                    # Define what parameters are allowed or not
                    response_parameters={
                        "method.response.header._content-_type": True,
                        "method.response.header._access-_control-_allow-_origin": True,
                    },
                ),
                apigw.MethodResponse(
                    # Same thing for the error responses
                    status_code="400",
                    response_parameters={
                        "method.response.header._content-_type": True,
                        "method.response.header._access-_control-_allow-_origin": True,
                    },
                ),
            ],
        )  # Creating/Updating a startup
        startup.add_method("GET", method_responses=[
                apigw.MethodResponse(
                    # Successful response from the integration
                    status_code="200",
                    # Define what parameters are allowed or not
                    response_parameters={
                        "method.response.header._content-_type": True,
                        "method.response.header._access-_control-_allow-_origin": True,
                    },
                ),
                apigw.MethodResponse(
                    # Same thing for the error responses
                    status_code="400",
                    response_parameters={
                        "method.response.header._content-_type": True,
                        "method.response.header._access-_control-_allow-_origin": True,
                    },
                ),
            ],)  # Get a startup

    def create_layer(self, lambda_name, entry: str) -> lambda_python.PythonLayerVersion:
        return lambda_python.PythonLayerVersion(
            self,
            lambda_name + "-layer",
            layer_version_name=lambda_name + "-layer",
            entry=entry,
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_7],
        )

    def create_lambda(self, lambda_name, layers=False):
        if layers:
            return _lambda.Function(
                self,
                lambda_name,
                function_name=lambda_name,
                handler=lambda_name + "." + LAMBDA_HANDLER_NAME,
                runtime=_lambda.Runtime.PYTHON_3_7,
                code=_lambda.Code.from_asset(LAMBDA_CODE_FOLDER),
                layers=[self.create_layer(lambda_name, LAMBDA_CODE_FOLDER)],
            )
        else:
            return _lambda.Function(
                self,
                lambda_name,
                function_name=lambda_name,
                handler=lambda_name + "." + LAMBDA_HANDLER_NAME,
                runtime=_lambda.Runtime.PYTHON_3_7,
                code=_lambda.Code.from_asset(LAMBDA_CODE_FOLDER),
            )
