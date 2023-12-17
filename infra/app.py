#!/usr/bin/env python3
import aws_cdk as cdk

from constants import PROJECT_NAME

from stacks.ecr_stack import ECRStack
from stacks.app_stack import AppStack

env = cdk.Environment(account="932785857088", region="eu-central-1")

app = cdk.App()

ecr_stack = ECRStack(app, "ECRStack", env=env, project_name=PROJECT_NAME)

AppStack(
    app,
    "AppStack",
    cpu=512,
    memory=1024,
    repo=ecr_stack.repo,
    env=env,
)

app.synth()
