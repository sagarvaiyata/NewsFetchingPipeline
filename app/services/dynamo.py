# app/services/dynamo.py
import boto3
from botocore.exceptions import ClientError
from app.config import DYNAMO_TABLE_NAME, AWS_REGION

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(DYNAMO_TABLE_NAME)

def url_exists(url: str) -> bool:
    try:
        response = table.get_item(Key={"url": url})
        return "Item" in response
    except ClientError as e:
        print(f"DynamoDB error: {e}")
        return False

def insert_doc(doc: dict):
    try:
        table.put_item(Item=doc)
    except ClientError as e:
        print(f"Failed to insert document: {e}")
