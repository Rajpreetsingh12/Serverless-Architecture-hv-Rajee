import boto3
from datetime import datetime, timezone, timedelta

# Initialize the EC2 client
ec2 = boto3.client('ec2')

def create_snapshot(volume_id, description='Snapshot created by Boto3 script'):
    """
    Create a snapshot for the specified EBS volume.
    
    Parameters:
    volume_id (str): The ID of the EBS volume
    description (str): A description for the snapshot
    
    Returns:
    dict: Information about the created snapshot
    """
    response = ec2.create_snapshot(VolumeId=vol-0ab08c37747d06f02, Description=description)
    return response

def list_snapshots(volume_id):
    """
    List all snapshots for the specified EBS volume.
    
    Parameters:
    volume_id (str): The ID of the EBS volume
    
    Returns:
    list: List of snapshots
    """
    snapshots = []
    response = ec2.describe_snapshots(Filters=[{'Name': 'volume-id', 'Values': [volume_id]}])
    
    while True:
        snapshots.extend(response['Snapshots'])
        
        if 'NextToken' in response:
            response = ec2.describe_snapshots(Filters=[{'Name': 'volume-id', 'Values': [volume_id]}], NextToken=response['NextToken'])
        else:
            break
    
    return snapshots

def delete_old_snapshots(snapshots, age_minutes=30):
    """
    Delete snapshots older than the specified number of minutes.
    
    Parameters:
    snapshots (list): List of snapshots to evaluate
    age_minutes (int): Number of minutes to determine if a snapshot is old
    
    Returns:
    list: List of deleted snapshot IDs
    """
    deleted_snapshots = []
    threshold_date = datetime.now(timezone.utc) - timedelta(minutes=age_minutes)
    
    for snapshot in snapshots:
        if snapshot['StartTime'] < threshold_date:
            ec2.delete_snapshot(SnapshotId=snapshot['SnapshotId'])
            deleted_snapshots.append(snapshot['SnapshotId'])
    
    return deleted_snapshots

def lambda_handler(event, context):
    """
    Lambda handler function to create a snapshot, list snapshots, delete old snapshots, and log the IDs.
    
    Parameters:
    event (dict): Event data passed by AWS services to Lambda
    context (object): Runtime information provided by AWS Lambda
    
    Returns:
    dict: Response with status code and body
    """
    volume_id = event.get('volume_id')
    
    if not volume_id:
        return {
            'statusCode': 400,
            'body': 'No volume ID provided in the event.'
        }
    
    # Create a snapshot
    snapshot = create_snapshot(volume_id)
    created_snapshot_id = snapshot['SnapshotId']
    
    # List all snapshots
    snapshots = list_snapshots(volume_id)
    
    # Delete old snapshots
    deleted_snapshots = delete_old_snapshots(snapshots)
    
    # Log the created and deleted snapshot IDs
    print(f"Created snapshot: {created_snapshot_id}")
    if deleted_snapshots:
        print("Deleted snapshots:")
        for snapshot_id in deleted_snapshots:
            print(snapshot_id)
    else:
        print("No snapshots older than 30 minutes were found.")
    
    return {
        'statusCode': 200,
        'body': {
            'created_snapshot_id': created_snapshot_id,
            'deleted_snapshot_ids': deleted_snapshots
        }
    }