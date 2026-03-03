#!/usr/bin/env python3
"""Upload PDF files to S3 bucket for Bedrock Knowledge Base."""

import boto3
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BUCKET_NAME = 'my-nova-rag-data'
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
ACCESS_KEY_ID = os.getenv('BEDROCK_UPLOAD_ACCESS_KEY_ID')
SECRET_ACCESS_KEY = os.getenv('BEDROCK_UPLOAD_SECRET_ACCESS_KEY')

def upload_pdf_to_s3(pdf_path):
    """Upload a PDF file to the S3 bucket."""
    
    # Validate file exists
    if not os.path.exists(pdf_path):
        print(f"❌ Error: File not found: {pdf_path}")
        return False
    
    # Validate it's a PDF
    if not pdf_path.lower().endswith('.pdf'):
        print(f"❌ Error: File must be a PDF: {pdf_path}")
        return False
    
    # Create S3 client with credentials from .env
    s3 = boto3.client(
        's3',
        region_name=AWS_REGION,
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=SECRET_ACCESS_KEY
    )
    
    # Get just the filename
    file_name = os.path.basename(pdf_path)
    
    try:
        print(f"Uploading {file_name} to s3://{BUCKET_NAME}/...")
        
        # Upload the PDF
        s3.upload_file(
            pdf_path,
            BUCKET_NAME,
            file_name,
            ExtraArgs={'ContentType': 'application/pdf'}
        )
        
        print(f"✅ Successfully uploaded {file_name}")
        print(f"   S3 URI: s3://{BUCKET_NAME}/{file_name}")
        return True
        
    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        return False

if __name__ == "__main__":
    # Check if PDF path was provided
    if len(sys.argv) < 2:
        print("Usage: python upload_to_s3.py <path_to_pdf>")
        print("Example: python upload_to_s3.py document.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    upload_pdf_to_s3(pdf_path)