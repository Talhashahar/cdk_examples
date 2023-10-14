from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_iam as iam
from aws_cdk import CfnOutput
from aws_cdk import aws_events as events
from aws_cdk import aws_events_targets as targets
from constructs import Construct
from cdk_examples.constructs.role_construct import RoleConstruct


class LambdaConstruct(Construct):

    def __init__(self, scope: Construct, id: str, env_vars: dict, lambda_name: str, handler_path: str,
                 aws_role: iam.Role = None, python_version: str = "python3.10",
                 code_location: str = "handler.lambda_handler", schedule_expression: str = None, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        if aws_role is None:
            aws_role = self.create_lambda_role(lambda_name)

        lambda_function = _lambda.Function(
            self,
            lambda_name,
            runtime=_lambda.Runtime(python_version),
            handler=handler_path,
            code=_lambda.Code.from_asset(code_location),
            environment=env_vars,
            role=aws_role,
        )

        if schedule_expression:
            # if not cron.CronExpression.isValidExpression(schedule_expression):
            #     raise ValueError("Invalid schedule_expression. Please provide a valid cron expression.")
            self.add_schedule(lambda_function, schedule_expression)

        CfnOutput(
            self,
            "LambdaFunctionArn",
            value=lambda_function.function_arn,
            description="Lambda Function ARN",
        )

    def create_lambda_role(self, lambda_name: str) -> iam.Role:
        lambda_role = RoleConstruct(
            self,
            "LambdaRole",
            role_name=f"{lambda_name}Policy")

        return lambda_role

    def add_schedule(self, lambda_function, schedule_expression: str):
        rule = events.Rule(
            self,
            "Rule",
            schedule=events.Schedule.expression(schedule_expression),
        )

        rule.add_target(targets.LambdaFunction(lambda_function))
