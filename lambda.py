import json
import boto3
import requests

# S3とSageMakerのクライアント
s3 = boto3.client('s3')
runtime_client = boto3.client('runtime.sagemaker')

def lambda_handler(event, context):
    try:
        # S3イベントからバケット名とファイル名を取得
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        file_name = event['Records'][0]['s3']['object']['key']
        
        # S3から画像をダウンロード
        response = s3.get_object(Bucket=bucket_name, Key=file_name)
        image_data = response['Body'].read()
        
        # SageMakerエンドポイントに画像データを送信
        endpoint_name = ''
