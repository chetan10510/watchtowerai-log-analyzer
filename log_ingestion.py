import boto3
import time
import datetime

# AWS region and log group/stream names
REGION = 'ap-south-1'
LOG_GROUP = '/watchtower/logs'
LOG_STREAM = 'test-stream-1'

# Create CloudWatch Logs client
logs_client = boto3.client('logs', region_name=REGION)

# Step 1: Create log stream (only once)
def create_log_stream():
    try:
        logs_client.create_log_stream(
            logGroupName=LOG_GROUP,
            logStreamName=LOG_STREAM
        )
        print(f" Created log stream: {LOG_STREAM}")
    except logs_client.exceptions.ResourceAlreadyExistsException:
        print(f" Log stream already exists: {LOG_STREAM}")

# Step 2: Send log events
def send_logs():
    timestamp = int(time.time() * 1000)
    messages = [
        "ERROR: Database connection failed",
        "INFO: User login success",
        "WARNING: High memory usage on instance",
        "CRITICAL: Payment gateway not responding"
    ]

    # You need the nextSequenceToken if logs already exist
    try:
        response = logs_client.describe_log_streams(
            logGroupName=LOG_GROUP,
            logStreamNamePrefix=LOG_STREAM
        )
        token = response['logStreams'][0].get('uploadSequenceToken', None)
    except Exception as e:
        print(" Error getting sequence token:", e)
        return

    # Send all messages
    log_events = [{
        'timestamp': timestamp + i * 1000,
        'message': msg
    } for i, msg in enumerate(messages)]

    kwargs = {
        'logGroupName': LOG_GROUP,
        'logStreamName': LOG_STREAM,
        'logEvents': log_events
    }

    if token:
        kwargs['sequenceToken'] = token

    response = logs_client.put_log_events(**kwargs)
    print(" Logs sent to CloudWatch")

if __name__ == "__main__":
    create_log_stream()
    send_logs()
