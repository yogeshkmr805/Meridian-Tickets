import os
import boto3
from botocore.exceptions import ClientError

TABLE_NAME = os.environ["INVENTORY_TABLE"]
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

def handler(event, context):
    seat_id = event["seat_id"]
    try:
        table.update_item(
            Key={"seat_id": seat_id},
            UpdateExpression="SET available = available - :one, seat_status = :held",
            ConditionExpression="available > :zero AND seat_status = :open",
            ExpressionAttributeValues={
                ":one": 1,
                ":zero": 0,
                ":held": "held",
                ":open": "open",
            },
        )
    except ClientError as err:
        if err.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return {"reserved": False, "reason": "seat_unavailable"}
        raise
    return {"reserved": True, "seat_id": seat_id}