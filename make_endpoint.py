import boto3
from sagemaker.model import Model
from sagemaker import get_execution_role
import time
from botocore.exceptions import ClientError

# SageMaker用ロール
role = "SageMakerExecutionRole"

# ECRイメージURI
image_uri = "615299769340.dkr.ecr.ap-northeast-1.amazonaws.com/grit-model:latest"

# SageMakerセッション
sagemaker_session = boto3.Session(region_name='ap-northeast-1').client('sagemaker')

# モデルを定義
model = Model(
    model_data=None,
    image_uri=image_uri,
    role=role,
    #sagemaker_session=sagemaker_session
)

# 既存のエンドポイントを削除
sagemaker_client = boto3.client('sagemaker', region_name='ap-northeast-1')
try:
    sagemaker_client.delete_endpoint(EndpointName='grit-endpoint')
    print("Existing endpoint deleted.")
except sagemaker_client.exceptions.ClientError as e:
    print(f"Error deleting endpoint: {e}")

# 既存のエンドポイント構成を削除
try:
    sagemaker_client.delete_endpoint_config(EndpointConfigName='grit-endpoint')
    print("Existing endpoint configuration deleted.")
except ClientError as e:
    if e.response['Error']['Code'] == 'ValidationException':
        print("Endpoint configuration does not exist or has already been deleted.")
    else:
        print(f"Error deleting endpoint configuration: {e}")

# エンドポイントをデプロイ
predictor = model.deploy(
    instance_type='ml.m4.16xlarge',  # GPUインスタンス
    initial_instance_count=1,
    endpoint_name='grit-endpoint', # エンドポイント名
    model_name='grit-model'
)

print("Endpoint created: grit-endpoint")
