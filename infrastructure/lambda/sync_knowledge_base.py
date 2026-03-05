"""
AWS Lambda function to automatically sync Bedrock Knowledge Base when S3 changes.

This function is triggered by S3 events (PUT, DELETE) and starts a Knowledge Base ingestion job.
"""

import json
import boto3
import os

# Environment variables (set in Lambda configuration)
KNOWLEDGE_BASE_ID = os.environ.get('KNOWLEDGE_BASE_ID')
DATA_SOURCE_ID = os.environ.get('DATA_SOURCE_ID')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# Initialize Bedrock Agent client
bedrock_agent = boto3.client('bedrock-agent', region_name=AWS_REGION)

def lambda_handler(event, context):
    """
    Lambda handler triggered by S3 events.
    
    Args:
        event: S3 event data
        context: Lambda context
    
    Returns:
        Response with status and ingestion job ID
    """
    
    print(f"Received event: {json.dumps(event)}")
    
    # Validate configuration
    if not KNOWLEDGE_BASE_ID or not DATA_SOURCE_ID:
        error_msg = "KNOWLEDGE_BASE_ID or DATA_SOURCE_ID not configured"
        print(f"ERROR: {error_msg}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': error_msg})
        }
    
    try:
        # Extract S3 event details
        records = event.get('Records', [])
        
        if not records:
            print("No records in event")
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'No records to process'})
            }
        
        # Get file details from first record
        s3_record = records[0]['s3']
        bucket = s3_record['bucket']['name']
        key = s3_record['object']['key']
        event_name = records[0]['eventName']
        
        print(f"S3 Event: {event_name}")
        print(f"Bucket: {bucket}")
        print(f"Key: {key}")
        
        # Start Knowledge Base ingestion job
        print(f"Starting ingestion job for Knowledge Base: {KNOWLEDGE_BASE_ID}")
        
        response = bedrock_agent.start_ingestion_job(
            knowledgeBaseId=KNOWLEDGE_BASE_ID,
            dataSourceId=DATA_SOURCE_ID,
            description=f"Auto-sync triggered by S3 event: {event_name} on {key}"
        )
        
        ingestion_job = response['ingestionJob']
        ingestion_job_id = ingestion_job['ingestionJobId']
        status = ingestion_job['status']
        
        print(f"✅ Ingestion job started successfully")
        print(f"Job ID: {ingestion_job_id}")
        print(f"Status: {status}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Knowledge Base sync triggered successfully',
                'ingestion_job_id': ingestion_job_id,
                'status': status,
                'triggered_by': {
                    'bucket': bucket,
                    'key': key,
                    'event': event_name
                }
            })
        }
        
    except Exception as e:
        error_msg = f"Error triggering Knowledge Base sync: {str(e)}"
        print(f"ERROR: {error_msg}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': error_msg,
                'knowledge_base_id': KNOWLEDGE_BASE_ID,
                'data_source_id': DATA_SOURCE_ID
            })
        }
