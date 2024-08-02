import boto3

# Initialize the EC2 client
ec2 = boto3.client('ec2')

# Define the tags
TAG_KEY = 'Action'
TAG_START_VALUE = 'auto-start'
TAG_STOP_VALUE = 'auto-stop'

def lambda_handler(event, context):
    """
    Handler function for AWS Lambda to start and stop EC2 instances based on tags.
    
    Parameters:
    event (dict): Event data passed by AWS services to Lambda
    context (object): Runtime information provided by AWS Lambda
    
    Returns:
    dict: Response with status code and body
    """
    # Get instances with auto-start and auto-stop tags
    auto_start_instances = describe_instances_by_tag(TAG_KEY, TAG_START_VALUE)
    auto_stop_instances = describe_instances_by_tag(TAG_KEY, TAG_STOP_VALUE)
    
    # Start auto-start instances
    if auto_start_instances:
        start_response = start_instances(auto_start_instances)
        print("Started instances:", auto_start_instances)
        print("Start response:", start_response)
    else:
        print("No instances found with tag Action=auto-start.")
    
    # Stop auto-stop instances
    if auto_stop_instances:
        stop_response = stop_instances(auto_stop_instances)
        print("Stopped instances:", auto_stop_instances)
        print("Stop response:", stop_response)
    else:
        print("No instances found with tag Action=auto-stop.")
    
    return {
        'statusCode': 200,
        'body': 'Instance start/stop operation completed.'
    }

def describe_instances_by_tag(tag_key, tag_value):
    """
    Describe instances that have a specific tag key and value.
    
    Parameters:
    tag_key (str): The tag key to filter by
    tag_value (str): The tag value to filter by
    
    Returns:
    list: List of instance IDs
    """
    response = ec2.describe_instances(
        Filters=[
            {'Name': f'tag:{tag_key}', 'Values': [tag_value]}
        ]
    )
    
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append(instance['InstanceId'])
    
    return instances

def start_instances(instance_ids):
    """
    Start the specified EC2 instances.
    
    Parameters:
    instance_ids (list): List of instance IDs to start
    
    Returns:
    dict: AWS response
    """
    response = ec2.start_instances(InstanceIds=instance_ids)
    return response

def stop_instances(instance_ids):
    """
    Stop the specified EC2 instances.
    
    Parameters:
    instance_ids (list): List of instance IDs to stop
    
    Returns:
    dict: AWS response
    """
    response = ec2.stop_instances(InstanceIds=instance_ids)
    return response
