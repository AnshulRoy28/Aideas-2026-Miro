#!/usr/bin/env python3
"""List all files in S3 bucket with their metadata."""

import boto3
import os
import json
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Configuration
BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'my-nova-rag-data')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
ACCESS_KEY_ID = os.getenv('BEDROCK_UPLOAD_ACCESS_KEY_ID')
SECRET_ACCESS_KEY = os.getenv('BEDROCK_UPLOAD_SECRET_ACCESS_KEY')

def list_s3_files_with_metadata():
    """List all files in the S3 bucket with their metadata."""
    
    # Create S3 client
    s3 = boto3.client(
        's3',
        region_name=AWS_REGION,
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=SECRET_ACCESS_KEY
    )
    
    try:
        print(f"\n📦 Listing files in bucket: {BUCKET_NAME}")
        print("=" * 80)
        
        # List all objects in the bucket
        response = s3.list_objects_v2(Bucket=BUCKET_NAME)
        
        if 'Contents' not in response:
            print("\n❌ No files found in bucket")
            return
        
        # Iterate through each object
        for idx, obj in enumerate(response['Contents'], 1):
            file_key = obj['Key']
            
            print(f"\n{idx}. File: {file_key}")
            print("-" * 80)
            
            # Get detailed metadata for each object
            metadata_response = s3.head_object(Bucket=BUCKET_NAME, Key=file_key)
            
            # Display basic object info
            print(f"   Size: {obj['Size']:,} bytes ({obj['Size'] / 1024:.2f} KB)")
            print(f"   Last Modified: {obj['LastModified']}")
            print(f"   ETag: {obj['ETag']}")
            
            # Display content type
            if 'ContentType' in metadata_response:
                print(f"   Content-Type: {metadata_response['ContentType']}")
            
            # Display storage class
            if 'StorageClass' in obj:
                print(f"   Storage Class: {obj['StorageClass']}")
            else:
                print(f"   Storage Class: STANDARD")
            
            # Display custom metadata (if any)
            if 'Metadata' in metadata_response and metadata_response['Metadata']:
                print(f"   Custom Metadata:")
                for key, value in metadata_response['Metadata'].items():
                    print(f"      {key}: {value}")
            else:
                print(f"   Custom Metadata: None")
            
            # Display additional headers
            if 'CacheControl' in metadata_response:
                print(f"   Cache-Control: {metadata_response['CacheControl']}")
            
            if 'ContentEncoding' in metadata_response:
                print(f"   Content-Encoding: {metadata_response['ContentEncoding']}")
            
            if 'ServerSideEncryption' in metadata_response:
                print(f"   Encryption: {metadata_response['ServerSideEncryption']}")
            
            # If this is a metadata.json file, show its contents
            if file_key.endswith('.metadata.json'):
                try:
                    obj_data = s3.get_object(Bucket=BUCKET_NAME, Key=file_key)
                    metadata_content = json.loads(obj_data['Body'].read().decode('utf-8'))
                    print(f"   📄 Metadata JSON Contents:")
                    print(f"      {json.dumps(metadata_content, indent=6)}")
                except Exception as e:
                    print(f"   ⚠️  Could not read metadata JSON: {e}")
        
        print("\n" + "=" * 80)
        print(f"✅ Total files: {len(response['Contents'])}")
        
    except Exception as e:
        print(f"\n❌ Error listing files: {e}")

if __name__ == "__main__":
    list_s3_files_with_metadata()
