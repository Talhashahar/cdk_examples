from constructs import Construct
from aws_cdk import aws_s3 as s3
from aws_cdk.aws_s3 import BlockPublicAccess, BucketAccessControl
from aws_cdk import aws_iam as iam
from aws_cdk import RemovalPolicy


class S3BucketConstruct(Construct):

    def __init__(self, scope: Construct, id: str, bucket_name, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Define the S3 bucket
        self.bucket_name = bucket_name
        self.bucket = s3.Bucket(self, self.bucket_name, bucket_name=self.bucket_name,
                                block_public_access=BlockPublicAccess.BLOCK_ALL,
                                access_control=BucketAccessControl.PRIVATE,
                                encryption=s3.BucketEncryption.S3_MANAGED,
                                versioned=True,
                                removal_policy=RemovalPolicy.RETAIN)

        # Define the Grantee principal
        grantee = iam.ArnPrincipal("arn:aws:iam::c4d8eabf8db69dbe46bfe0e517100c554f01200b104d59cd408e777ba442a322")

        # Grant read and write permissions to the Grantee
        self.bucket.grant_read(grantee)
        self.bucket.grant_write(grantee)
