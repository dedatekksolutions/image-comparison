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

        # Check if the file exists in approved folder
        approved_key = approved_prefix + filename
        try:
            s3.head_object(Bucket=approved_bucket, Key=approved_key)
            # If file exists in approved folder, update status to 'approved'
            update_status(dynamodb, table_name, key_attribute_name, key_value, "approved")
        except Exception as e:
            # If file doesn't exist in approved folder, update status to 'preapproved'
            update_status(dynamodb, table_name, key_attribute_name, key_value, "preapproved")
            print(f"File {filename} not found in approved folder. Status updated to 'preapproved'.")

    print(f"Status updated for the provided filenames: {filenames}")
    return {
        "statusCode": 200,
        "body": json.dumps({"message": f"Status updated for the provided filenames: {filenames}"})
    }

def update_status(dynamodb, table_name, key_attribute_name, key_value, new_status):
    try:
        response = dynamodb.update_item(
            TableName=table_name,
            Key={key_attribute_name: {'S': key_value}},
            UpdateExpression="SET #statusAttr = :statusValue",
            ExpressionAttributeNames={"#statusAttr": "status"},
            ExpressionAttributeValues={":statusValue": {"S": new_status}},
            ReturnValues="UPDATED_NEW"
        )
        print(f"DynamoDB Update Response for {key_value}: {response}")
    except Exception as e:
        print(f"Error updating status for {key_value}: {e}")
