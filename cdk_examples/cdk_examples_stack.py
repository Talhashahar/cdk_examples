from aws_cdk import Stack
from aws_cdk import aws_iam as iam
from constructs import Construct

from cdk_examples.constructs.lambda_construct import LambdaConstruct
from cdk_examples.constructs.role_construct import RoleConstruct
from cdk_examples.constructs.s3_constrcut import S3BucketConstruct
from cdk_examples.constructs.dynamodb_constrcut import DynamodbConstruct
from cdk_examples.consts import BUCKET_NAME, DYNAMODB_TABLE_NAME, CRON_PATTERN


class CdkExamplesStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self._create_bucket()
        self._create_ddb_table()
        self._create_lambda(lambda_name="first_lambda", lambda_path="handler.lambda_handler", schedule_expression=CRON_PATTERN)
        self._create_lambda(lambda_name="second_lambda", lambda_path="handler.lambda_handler")

    def _create_bucket(self):
        self.bucket = S3BucketConstruct(self,
                                        BUCKET_NAME,
                                        bucket_name=BUCKET_NAME)

    def _create_ddb_table(self):
        self.table = DynamodbConstruct(self, DYNAMODB_TABLE_NAME, table_name=DYNAMODB_TABLE_NAME)

    def _create_lambda(self, lambda_name: str, lambda_path: str, schedule_expression: str = None):
        lambda_role = RoleConstruct(
            self,
            f"{lambda_name}LambdaRole",
            role_name="LambdaRoleWithS3Access",
            custom_policies=[  # Attach S3 access policy
                iam.PolicyStatement(
                    actions=["s3:GetObject", "s3:PutObject"],
                    resources=[self.bucket.bucket.bucket_arn],
                ),
                iam.PolicyStatement(
                    actions=["dynamodb:BatchGet*",
                             "dynamodb:DescribeStream",
                             "dynamodb:DescribeTable",
                             "dynamodb:Get*",
                             "dynamodb:Query",
                             "dynamodb:Scan",
                             "dynamodb:BatchWrite*",
                             "dynamodb:CreateTable",
                             "dynamodb:Delete*",
                             "dynamodb:Update*",
                             "dynamodb:PutItem"],
                    resources=[self.table.table.table_arn],
                ),
            ],
        )

        self.lambda_construct = LambdaConstruct(
            self,
            f"{lambda_name}LambdaFunction",
            env_vars={"BUCKET_ARN": self.bucket.bucket.bucket_arn, "BUCKET_NAME": BUCKET_NAME},
            lambda_name=lambda_name,
            handler_path=lambda_path,
            aws_role=lambda_role.role,
            code_location=f"lambdas/{lambda_name}/",
            schedule_expression=schedule_expression
        )
