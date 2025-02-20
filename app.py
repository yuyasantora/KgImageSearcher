from aws_cdk import (
    aws_ec2 as ec2,
    Stack,
    App,
    CfnOutput,
    aws_iam as iam,
    aws_s3 as s3s
)

import os

class Ec2ForDL2(Stack):

    def __init__(self, scope: App, name: str, key_name: str, **kwargs) -> None:
        super().__init__(scope, name, **kwargs)

        vpc = ec2.Vpc(
            self, "Ec2ForDl-Vpc",
            max_azs=1,
            cidr="10.10.0.0/23",
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                )
            ],
            nat_gateways=0,
        )

        sg = ec2.SecurityGroup(
            self, "Ec2ForDl-Sg",
            vpc=vpc,
            allow_all_outbound=True,
        )
        sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(22),
        )

        host = ec2.Instance(
            self, "Ec2ForDl-Instance",
            instance_type=ec2.InstanceType("g4dn.2xlarge"), # <1>
            machine_image=ec2.MachineImage.generic_linux({
                #"us-east-1": "ami-060f07284bb6f9faf",
                "ap-northeast-1": "ami-001a9ab9792bd35d3"
            }), # <2>
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=sg,
            key_name=key_name
        )
        host.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")
        )


        # print the server address
        CfnOutput(self, "InstancePublicDnsName", value=host.instance_public_dns_name)
        CfnOutput(self, "InstancePublicIp", value=host.instance_public_ip)

app = App()
Ec2ForDL2(
    app, "Ec2ForDL2",
    key_name=app.node.try_get_context("key_name"),
    env={
        "region": "ap-northeast-1",
        "account": os.environ["CDK_DEFAULT_ACCOUNT"],
    }
)

app.synth()
