#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk_examples.cdk_examples_stack import CdkExamplesStack


app = cdk.App()
CdkExamplesStack(app, "CdkExamplesStack",
    )

app.synth()
