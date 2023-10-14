from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
)
from aws_cdk import RemovalPolicy
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_iam as iam

from constructs import Construct
from cdk_examples.constructs.lambda_construct import LambdaConstruct
from cdk_examples.constructs.role_construct import RoleConstruct
from cdk_examples.constructs.s3_constrcut import S3BucketConstruct


class CdkExamplesStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket_name = "exmaplebucketnameth"  # Replace with your S3 bucket name
        self.bucket = S3BucketConstruct(self,
                                        bucket_name,
                                        bucket_name=bucket_name)
        self.lambda_role_construct = RoleConstruct(
            self,
            "LambdaRole",
            role_name="LambdaRoleWithS3Access",
            custom_policies=[  # Attach S3 access policy
                    iam.PolicyStatement(
                        actions=["s3:GetObject", "s3:PutObject"],
                        resources=[f"arn:aws:s3:::{bucket_name}/*"],
                    ),
            ],
        )
        self.lambda_construct = LambdaConstruct(
            self,
            "MyLambdaFunction",
            env_vars={"BUCKET_ARN": self.bucket.bucket.bucket_arn, "BUCKET_NAME": bucket_name},  # Replace with your environment variables
            lambda_name="FirstLambda",
            handler_path="handler.lambda_handler",  # Replace with your Lambda handler path
            aws_role=self.lambda_role_construct.lambda_role,
            code_location="lambdas/first_lambda/",  # Replace with your code location
        )
