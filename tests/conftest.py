import os

import boto3
import pytest
from moto import mock_aws


@pytest.fixture
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-1"

@pytest.fixture
def aws_setup(aws_credentials):
    with mock_aws():
        kinesis_client = boto3.client("kinesis")
        kinesis_client.create_stream(StreamName="logsentinel-stream", ShardCount=1)

        ssm_client = boto3.client("ssm")
        ssm_client.put_parameter(
            Name="/logsentinel/stream-name",
            Value="logsentinel-stream",
            Type="String"
            )
        yield kinesis_client, ssm_client

