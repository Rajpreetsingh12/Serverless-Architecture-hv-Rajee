import boto3

# Initialize the S3 client
s3 = boto3.client('s3')

def list_buckets():
    """
    List all S3 buckets.
    
    Returns:
    list: List of bucket names
    """
    response = s3.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    return buckets

def check_bucket_encryption(bucket_name):
    """
    Check if the specified S3 bucket has server-side encryption enabled.
    
    Parameters:
    bucket_name (str): The name of the S3 bucket
    
    Returns:
    bool: True if encryption is enabled, False otherwise
    """
    try:
        s3.get_bucket_encryption(Bucket=bucket_name)
        return True
    except s3.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
            return False
        else:
            raise

def lambda_handler(event, context):
    """
    Lambda handler function to list all S3 buckets, detect unencrypted buckets, and log their names.
    
    Parameters:
    event (dict): Event data passed by AWS services to Lambda
    context (object): Runtime information provided by AWS Lambda
    
    Returns:
    dict: Response with status code and body
    """
    # List all buckets
    buckets = list_buckets()
    unencrypted_buckets = []

    # Check each bucket for encryption
    for bucket in buckets:
        if not check_bucket_encryption(bucket):
            unencrypted_buckets.append(bucket)

    # Log the names of unencrypted buckets
    if unencrypted_buckets:
        print("Unencrypted buckets:")
        for bucket in unencrypted_buckets:
            print(bucket)
        return {
            'statusCode': 200,
            'body': f"Unencrypted buckets: {', '.join(unencrypted_buckets)}"
        }
    else:
        print("All buckets have server-side encryption enabled.")
        return {
            'statusCode': 200,
            'body': "All buckets have server-side encryption enabled."
        }
