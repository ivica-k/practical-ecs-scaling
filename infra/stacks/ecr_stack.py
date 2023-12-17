from aws_cdk import aws_ecr as ecr, Stack, RemovalPolicy, CfnOutput
from constructs import Construct


class ECRStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, project_name: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.repo = ecr.Repository(
            self,
            "repo",
            image_scan_on_push=False,
            repository_name=f"{project_name}",
            removal_policy=RemovalPolicy.DESTROY,
        )

        CfnOutput(self, "RepoName", value=self.repo.repository_name)
