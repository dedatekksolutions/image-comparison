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

        # Check if the item exists in DynamoDB
        try:
            response = dynamodb.get_item(
                TableName=table_name,
                Key={key_attribute_name: {'S': key_value}}
            )
            item = response.get('Item')
            if item:
                # Item exists, update its status to 'declined'
                update_expression = "SET #statusAttr = :statusValue"
                expression_attribute_names = {"#statusAttr": "status"}
                expression_attribute_values = {":statusValue": {"S": "declined"}}
            else:
                # Item doesn't exist, update status to 'pre-approved'
                update_expression = "SET #statusAttr = :statusValue"
                expression_attribute_names = {"#statusAttr": "status"}
                expression_attribute_values = {":statusValue": {"S": "pre-approved"}}

            # Perform the update operation
            response = dynamodb.update_item(
                TableName=table_name,
                Key={key_attribute_name: {'S': key_value}},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="UPDATED_NEW"  # Modify as needed
            )
            print(f"DynamoDB Update Response for filename {filename}: {response}")

        except Exception as e:
            print(f"Error updating status for filename {filename}: {e}")

    print(f"Status updated for the provided filenames: {filenames}")
    return {
        "statusCode": 200,
        "body": json.dumps({"message": f"Status updated for the provided filenames: {filenames}"})
    }
