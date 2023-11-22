import boto3
import hashlib
import json

def lambda_handler(event, context):
    # Update bucket names and paths
    approved_bucket = 'retroideal-member-vehicle-images'
    approved_prefix = 'approved-vehicle-images/'

    pending_bucket = 'retroideal-member-vehicle-images'
    pending_prefix = 'pending-vehicle-images/'

    # Update DynamoDB table name
    table_name = 'retroideal-vehicle-image-table'

    # Create S3 and DynamoDB clients
    s3 = boto3.client('s3')
    dynamodb = boto3.client('dynamodb')

    # Check if the event is from API Gateway
    if 'body' in event:
        payload = json.loads(event['body'])
    else:
        # For local testing
        payload = event

    filenames = payload.get('filename', [])

    print(f"Received filenames: {filenames}")

    for filename in filenames:
        # Construct the DynamoDB key based on the primary key attribute
        key_attribute_name = 'image-id'
        key_value = filename

        # Update DynamoDB DeleteItem operation to use the correct key
        try:
            response = dynamodb.delete_item(
                TableName=table_name,
                Key={key_attribute_name: {'S': key_value}}
            )
            print(f"DynamoDB Delete Response for filename {filename}: {response}")

        except Exception as e:
            print(f"Error deleting item for filename {filename}: {e}")

    print(f"Items deleted for the provided filenames: {filenames}")
    return {
        "statusCode": 200,
        "body": json.dumps({"message": f"Items deleted for the provided filenames: {filenames}"})
    }
