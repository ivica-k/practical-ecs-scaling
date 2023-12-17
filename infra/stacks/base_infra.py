from aws_cdk import (
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as lb,
)

from constructs import Construct


class BaseInfra(Construct):
    def __init__(self, scope: Construct, construct_id: str, project_name: str) -> None:
        super().__init__(scope, construct_id)
        self.project_name = project_name

        self.vpc = self._create_vpc()
        self.cluster = self._create_cluster(vpc=self.vpc)
        self.alb = self._create_alb(vpc=self.vpc)

        self.listener = self.alb.add_listener("listener", port=80)

    def _create_vpc(self):
        return ec2.Vpc(
            self,
            id="vpc",
            ip_addresses=ec2.IpAddresses.cidr("10.255.0.0/16"),
            max_azs=2,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name=f"{self.project_name}-subnet-public",
                    cidr_mask=24,
                    reserved=False,
                    subnet_type=ec2.SubnetType.PUBLIC,
                ),
                ec2.SubnetConfiguration(
                    name=f"{self.project_name}-subnet-private",
                    cidr_mask=24,
                    reserved=False,
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                ),
            ],
            enable_dns_hostnames=True,
            enable_dns_support=True,
        )

    def _create_cluster(self, vpc: ec2.Vpc):
        return ecs.Cluster(
            self,
            "ecs_cluster",
            cluster_name=f"{self.project_name}-cluster",
            vpc=vpc,
        )

    def _create_alb(self, vpc: ec2.Vpc):
        return lb.ApplicationLoadBalancer(
            self,
            "lb",
            vpc=vpc,
            internet_facing=True,
            load_balancer_name=f"{self.project_name}-alb",
        )
