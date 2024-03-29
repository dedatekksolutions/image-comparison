import boto3
import hashlib
import json

def lambda_handler(event, context):
    # Update bucket names and paths
    approved_bucket = 'retroideal-member-vehicle-images'
    approved_prefix = 'approved-vehicle-images/'

    pending_bucket = 'retroideal-member-vehicle-images'
    pending_prefix = 'pending-vehicle-images/'

    # Create S3 and DynamoDB clients
    s3 = boto3.client('s3')
    dynamodb = boto3.client('dynamodb')

    # Get the filename from the event
    payload = json.loads(event['body']) if 'body' in event else None
    filename = payload.get('filename') if payload else None

    if filename:
        # Retrieve the content of the pending image
        pending_object_data = s3.get_object(Bucket=pending_bucket, Key=pending_prefix + filename)
        pending_content = pending_object_data['Body'].read()

        # Get the list of objects in the approved bucket
        approved_objects = s3.list_objects_v2(Bucket=approved_bucket, Prefix=approved_prefix)['Contents']

        # Flag to check if any match found
        match_found = False

        # Compare each object in the approved bucket with the pending image
        for approved_object in approved_objects:
            approved_key = approved_object['Key']

            # Skip if the object is a folder
            if approved_key.endswith('/'):
                continue

            # Retrieve the content of the approved image
            approved_object_data = s3.get_object(Bucket=approved_bucket, Key=approved_key)
            approved_content = approved_object_data['Body'].read()

            # Compare image content using hash
            if hashlib.md5(pending_content).hexdigest() == hashlib.md5(approved_content).hexdigest():
                match_found = True
                break  # Found a match, no need to continue searching

        # Update status in DynamoDB based on match
        table_name = 'retroideal-member-vehicle-images'
        status = 'preapproved' if not match_found else 'declined'

        dynamodb.update_item(
            TableName=table_name,
            Key={'filename': {'S': filename}},
            UpdateExpression='SET #s = :status',
            ExpressionAttributeNames={'#s': 'status'},
            ExpressionAttributeValues={':status': {'S': status}}
        )

        return f"Status updated to {status}"

    return "Filename not provided in payload"
