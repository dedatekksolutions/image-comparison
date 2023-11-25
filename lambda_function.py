import boto3
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
        # Query DynamoDB to find the item with matching filename
        try:
            response = dynamodb.scan(
                TableName=table_name,
                FilterExpression='filename = :filename',
                ExpressionAttributeValues={':filename': {'S': filename}}
            )

            # Check if there's a matching item
            if response['Count'] > 0:
                image_id = response['Items'][0]['image-id']['S']

                # Update DynamoDB UpdateItem operation to set status to 'approved' using image-id
                update_response = dynamodb.update_item(
                    TableName=table_name,
                    Key={'image-id': {'S': image_id}},
                    UpdateExpression='SET #status = :status',
                    ExpressionAttributeNames={'#status': 'status'},
                    ExpressionAttributeValues={':status': {'S': 'approved'}}
                )
                print(f"DynamoDB Update Response for filename {filename}: {update_response}")
            else:
                print(f"No item found for filename {filename}")

        except Exception as e:
            print(f"Error processing filename {filename}: {e}")

    print(f"Status updated to 'approved' for the provided filenames: {filenames}")
    return {
        "statusCode": 200,
        "body": json.dumps({"message": f"Status updated to 'approved' for the provided filenames: {filenames}"})
    }
