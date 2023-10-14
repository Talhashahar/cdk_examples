from constructs import Construct
from aws_cdk import aws_dynamodb as dynamodb


class DynamodbConstruct(Construct):

    def __init__(self, scope: Construct, id: str, table_name: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Define the S3 bucket
        self.table = dynamodb.TableV2(self, table_name,
                                 table_name=table_name,
                                 partition_key=dynamodb.Attribute(name="task_id", type=dynamodb.AttributeType.STRING),
                                 contributor_insights=True,
                                 table_class=dynamodb.TableClass.STANDARD_INFREQUENT_ACCESS,
                                 point_in_time_recovery=True
                                 )
