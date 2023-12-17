from aws_cdk import Stack
from constructs import Construct
from .containerized_app import ContainerizedApp
from constants import PROJECT_NAME
from .base_infra import BaseInfra

from aws_cdk import (
    aws_ecr as ecr,
    CfnOutput,
)


class AppStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        repo: ecr.Repository,
        cpu: int,
        memory: int,
        num_containers: int = 1,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        base_infra = BaseInfra(self, "baseinfra", PROJECT_NAME)

        ContainerizedApp(
            self,
            "app",
            PROJECT_NAME,
            repo=repo,
            cluster=base_infra.cluster,
            vpc=base_infra.vpc,
            listener=base_infra.listener,
            cpu=cpu,
            memory=memory,
            num_containers=num_containers,
        )

        CfnOutput(self, "ALB", value=f"http://{base_infra.alb.load_balancer_dns_name}")
