import boto3
import hashlib

def lambda_handler(event, context):
    # Update bucket names and paths
    approved_bucket = 'retroideal-member-vehicle-images'
    approved_prefix = 'approved-vehicle-images/'

    pending_bucket = 'retroideal-member-vehicle-images'
    pending_prefix = 'pending-vehicle-images/'

    # Create S3 clients
    s3 = boto3.client('s3')

    # Get the list of objects in each bucket with specified prefixes
    approved_objects = s3.list_objects_v2(Bucket=approved_bucket, Prefix=approved_prefix)['Contents']
    pending_objects = s3.list_objects_v2(Bucket=pending_bucket, Prefix=pending_prefix)['Contents']

    # Compare each object in the pending bucket with the approved bucket
    for pending_object in pending_objects:
        pending_key = pending_object['Key']

        # Skip if the object is a folder
        if pending_key.endswith('/'):
            continue

        # Retrieve the content of the pending image
        pending_object_data = s3.get_object(Bucket=pending_bucket, Key=pending_key)
        pending_content = pending_object_data['Body'].read()

        # Iterate through approved images and compare content
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
                return "Match"

    return "Different"
