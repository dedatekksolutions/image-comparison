
import hashlib
import boto3
from PIL import Image
import imagehash
import json

def lambda_handler(event, context):
    # Extract payload data
    if 'body' in event:
        payload = json.loads(event['body'])
    else:
        payload = event.get('queryStringParameters', {})

    filenames = payload.get('filename', [])

    # Define bucket names and table name
    pending_images_bucket = 'retroideal-member-vehicle-images'
    approved_images_bucket = 'retroideal-member-vehicle-images'
    vehicle_image_table = 'retroideal-vehicle-image-table'

    # Compare images in pending and approved folders
    for filename in filenames:
        pending_image_key = f"pending-vehicle-images/{filename}.jpg"
        approved_image_keys = get_all_approved_image_keys(approved_images_bucket)

        matching = False
        pending_hash = get_image_hash(pending_images_bucket, pending_image_key)

        for approved_key in approved_image_keys:
            approved_hash = get_image_hash(approved_images_bucket, approved_key)
            if pending_hash - approved_hash < 5:  # Adjust threshold as needed
                matching = True
                break

        # Update vehicle image table based on matching
        update_status_in_vehicle_image_table(vehicle_image_table, filename, matching)

    return {
        'statusCode': 200,
        'body': json.dumps('Images compared and vehicle image table updated.')
    }

def get_image_hash(bucket_name, image_key):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=image_key)
    image = Image.open(response['Body'])
    return imagehash.phash(image)

def get_all_approved_image_keys(bucket_name):
    s3 = boto3.client('s3')
    objects = s3.list_objects_v2(Bucket=bucket_name, Prefix='approved-vehicle-images/')
    approved_keys = [obj['Key'] for obj in objects.get('Contents', [])]
    return approved_keys

def compare_images(bucket1, key1, bucket2, key2):
    s3 = boto3.client('s3')
    image1 = s3.get_object(Bucket=bucket1, Key=key1)['Body'].read()
    image2 = s3.get_object(Bucket=bucket2, Key=key2)['Body'].read()

    # Compare image hashes using hashlib
    hash1 = hashlib.sha256(image1).hexdigest()
    hash2 = hashlib.sha256(image2).hexdigest()

    return hash1 == hash2

def update_status_in_vehicle_image_table(table_name, filename, matching):
    dynamodb = boto3.client('dynamodb')

    # Define the status based on matching
    status = 'declined' if matching else 'preapproved'

    # Update the status in the table
    try:
        response = dynamodb.update_item(
            TableName=table_name,
            Key={'filename': {'S': filename}},
            UpdateExpression='SET #s = :status',
            ExpressionAttributeNames={'#s': 'status'},
            ExpressionAttributeValues={':status': {'S': status}}
        )
        print(f"Status updated for filename: {filename} -> {status}")
    except Exception as e:
        print(f"Error updating status for filename {filename}: {e}")

    return

