from aws_cdk import (
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_ecr as ecr,
    aws_elasticloadbalancingv2 as lb,
    aws_logs as log,
    RemovalPolicy,
    Duration,
)
from constructs import Construct


class ContainerizedApp(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        project_name: str,
        repo: ecr.Repository,
        cluster: ecs.Cluster,
        vpc: ec2.Vpc,
        listener: lb.ApplicationListener,
        cpu: int = 512,
        memory: int = 1024,
        num_containers: int = 1,
    ):
        super().__init__(scope, id)
        self.project_name = project_name

        self._create_containers(
            cluster=cluster,
            vpc=vpc,
            listener=listener,
            repo=repo,
            cpu=cpu,
            memory=memory,
            num_containers=num_containers,
        )

    def _create_containers(
        self,
        cluster: ecs.Cluster,
        vpc: ec2.Vpc,
        listener: lb.ApplicationListener,
        repo: ecr.Repository,
        cpu: int,
        memory: int,
        num_containers: int,
    ):
        task_def = ecs.FargateTaskDefinition(
            self,
            "taskdef",
            family=self.project_name,
            cpu=cpu,
            memory_limit_mib=memory,
        )

        service = ecs.FargateService(
            self,
            "service",
            cluster=cluster,
            task_definition=task_def,
            desired_count=num_containers,
        )

        log_group = log.LogGroup(
            self,
            "log_group",
            retention=log.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY,
        )

        ecs.ContainerDefinition(
            self,
            "container",
            task_definition=task_def,
            container_name="vertical",
            environment={"ENV": "dev"},
            port_mappings=[
                ecs.PortMapping(container_port=5000, protocol=ecs.Protocol.TCP)
            ],
            image=ecs.ContainerImage.from_ecr_repository(repo, "latest"),
            logging=ecs.LogDrivers.aws_logs(stream_prefix="ecs", log_group=log_group),
            essential=True,
            command=[
                "python",
                "app.py",
            ],
        )

        target_group = lb.ApplicationTargetGroup(
            self,
            "tg",
            targets=[service],
            protocol=lb.ApplicationProtocol.HTTP,
            vpc=vpc,
        )

        listener.add_target_groups(
            "listener",
            target_groups=[target_group],
        )

        scaling = service.auto_scale_task_count(max_capacity=5)

        scaling.scale_to_track_custom_metric(
            "response_scaling",
            metric=target_group.metrics.target_response_time(
                period=Duration.minutes(1)
            ),
            target_value=2,
            scale_in_cooldown=Duration.minutes(1),
            scale_out_cooldown=Duration.minutes(1),
        )
