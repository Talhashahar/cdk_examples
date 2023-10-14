from constructs import Construct
from aws_cdk import aws_iam as iam, CfnOutput
from typing import List
from aws_cdk import aws_logs as logs


class RoleConstruct(Construct):

    def __init__(self, scope: Construct, id: str, role_name: str, custom_policies: List[iam.PolicyStatement] = None, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.role_name = role_name
        # Define the IAM role for the Lambda function
        self.role = iam.Role(
            self,
            f"{role_name}Role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            role_name=role_name
        )

        if custom_policies:
            for policy in custom_policies:
                self.role.add_to_policy(policy)

        # Output the IAM role ARN
        CfnOutput(
            self,
            "LambdaRoleArn",
            value=self.role.role_arn,
            description="Lambda Execution Role ARN",
        )

    @staticmethod
    def _add_default_policy(self):
        # Allow creating log groups with the Lambda name
        log_group_pattern = f"/aws/lambda/{self.role_name}"
        log_group_arn = f"arn:aws:logs:{core.Aws.REGION}:{core.Aws.ACCOUNT_ID}:log-group:{log_group_pattern}:*"
        self.role.add_to_policy(
            iam.PolicyStatement(
                actions=["logs:CreateLogGroup"],
                resources=[log_group_arn],
            )
        )

        self.role.add_to_policy(
            iam.PolicyStatement(
                actions=["logs:CreateLogStream", "logs:PutLogEvents"],
                resources=[f"{log_group_arn}:*"],
            )
        )