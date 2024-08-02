import boto3
from datetime import datetime, timezone, timedelta

# Initialize the S3 client
s3 = boto3.client('s3')

# Define the bucket name
BUCKET_NAME = 'lambdaserverlessrajee'

def list_objects(bucket_name):
    """
    List all objects in the specified S3 bucket.
    
    Parameters:
    bucket_name (str): The name of the S3 bucket
    
    Returns:
    list: List of objects in the bucket
    """
    objects = []
    response = s3.list_objects_v2(Bucket=bucket_name)
    
    while True:
        for obj in response.get('Contents', []):
            objects.append(obj)
        
        if response.get('IsTruncated'):  # More objects to retrieve
            response = s3.list_objects_v2(Bucket=bucket_name, ContinuationToken=response['NextContinuationToken'])
        else:
            break
    
    return objects

def delete_old_objects(bucket_name, objects, days=0):
    """
    Delete objects older than the specified number of days.
    
    Parameters:
    bucket_name (str): The name of the S3 bucket
    objects (list): List of objects to evaluate
    days (int): Number of days to determine if an object is old
    
    Returns:
    list: List of deleted object keys
    """
    deleted_objects = []
    threshold_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    for obj in objects:
        if obj['LastModified'] < threshold_date:
            s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
            deleted_objects.append(obj['Key'])
    
    return deleted_objects

def lambda_handler(event, context):
    """
    Lambda handler function to list objects, delete old objects, and log the names of deleted objects.
    
    Parameters:
    event (dict): Event data passed by AWS services to Lambda
    context (object): Runtime information provided by AWS Lambda
    
    Returns:
    dict: Response with status code and body
    """
    # List objects in the bucket
    objects = list_objects(BUCKET_NAME)
    
    if not objects:
        print(f"No objects found in bucket {BUCKET_NAME}.")
        return {
            'statusCode': 200,
            'body': f"No objects found in bucket {BUCKET_NAME}."
        }
    
    # Delete old objects
    deleted_objects = delete_old_objects(BUCKET_NAME, objects)
    
    if deleted_objects:
        print("Deleted objects:")
        for obj_key in deleted_objects:
            print(obj_key)
        return {
            'statusCode': 200,
            'body': f"Deleted objects: {', '.join(deleted_objects)}"
        }
    else:
        print(f"No objects older than 30 days were found in bucket {BUCKET_NAME}.")
        return {
            'statusCode': 200,
            'body': f"No objects older than 30 days were found in bucket {BUCKET_NAME}."
        }
