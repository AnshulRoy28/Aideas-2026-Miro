#!/usr/bin/env python3
"""Upload PDF files to S3 bucket with metadata for Miro Knowledge Base."""

import boto3
import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'my-nova-rag-data')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
ACCESS_KEY_ID = os.getenv('BEDROCK_UPLOAD_ACCESS_KEY_ID')
SECRET_ACCESS_KEY = os.getenv('BEDROCK_UPLOAD_SECRET_ACCESS_KEY')

def check_file_exists(s3, file_name):
    """Check if a file already exists in S3."""
    try:
        s3.head_object(Bucket=BUCKET_NAME, Key=file_name)
        return True
    except s3.exceptions.ClientError:
        return False

def upload_pdf_with_metadata(pdf_path, class_num, subject):
    """Upload a PDF file with metadata to the S3 bucket."""
    
    # Validate file exists
    if not os.path.exists(pdf_path):
        print(f"❌ Error: File not found: {pdf_path}")
        return False
    
    # Validate it's a PDF
    if not pdf_path.lower().endswith('.pdf'):
        print(f"❌ Error: File must be a PDF: {pdf_path}")
        return False
    
    # Validate class and subject
    if not class_num or not subject:
        print(f"❌ Error: Class and subject are required")
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
        # Check if file already exists in S3
        if check_file_exists(s3, file_name):
            print(f"\n⚠️  Warning: A file with the name '{file_name}' already exists in the bucket")
            response = input("Do you want to overwrite it? (yes/no): ").strip().lower()
            
            if response not in ['yes', 'y']:
                print("❌ Upload cancelled")
                return False
            
            print("📝 Overwriting existing file...")
        
        print(f"\n📤 Uploading {file_name} to s3://{BUCKET_NAME}/...")
        print(f"   Class: {class_num}")
        print(f"   Subject: {subject}")
        
        # Upload the PDF
        s3.upload_file(
            pdf_path,
            BUCKET_NAME,
            file_name,
            ExtraArgs={'ContentType': 'application/pdf'}
        )
        
        # Create metadata JSON
        metadata = {
            "metadataAttributes": {
                "class": str(class_num),
                "subject": subject
            }
        }
        
        metadata_key = f"{file_name}.metadata.json"
        
        # Upload metadata
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=metadata_key,
            Body=json.dumps(metadata),
            ContentType='application/json'
        )
        
        print(f"✅ Successfully uploaded {file_name}")
        print(f"✅ Successfully uploaded {metadata_key}")
        print(f"   S3 URI: s3://{BUCKET_NAME}/{file_name}")
        return True
        
    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        return False

def interactive_upload():
    """Interactive mode for uploading files."""
    print("\n" + "="*60)
    print("📚 MIRO - PDF Upload with Metadata")
    print("="*60 + "\n")
    
    # Get PDF path
    pdf_path = input("Enter the path to your PDF file: ").strip()
    
    if not pdf_path:
        print("❌ No file path provided")
        return False
    
    # Get class number
    class_num = input("Enter the class number (e.g., 1, 2, 10): ").strip()
    
    if not class_num:
        print("❌ Class number is required")
        return False
    
    # Get subject
    print("\nAvailable subjects:")
    subjects = [
        "Mathematics", "Physics", "Chemistry", "Biology",
        "English", "History", "Geography", "Computer Science", "General"
    ]
    for i, subj in enumerate(subjects, 1):
        print(f"  {i}. {subj}")
    
    subject_choice = input("\nEnter subject number or name: ").strip()
    
    # Parse subject choice
    if subject_choice.isdigit():
        idx = int(subject_choice) - 1
        if 0 <= idx < len(subjects):
            subject = subjects[idx]
        else:
            print("❌ Invalid subject number")
            return False
    else:
        subject = subject_choice
    
    # Confirm upload
    print(f"\n📋 Upload Summary:")
    print(f"   File: {os.path.basename(pdf_path)}")
    print(f"   Class: {class_num}")
    print(f"   Subject: {subject}")
    
    confirm = input("\nProceed with upload? (yes/no): ").strip().lower()
    
    if confirm not in ['yes', 'y']:
        print("❌ Upload cancelled")
        return False
    
    return upload_pdf_with_metadata(pdf_path, class_num, subject)

if __name__ == "__main__":
    if len(sys.argv) == 4:
        # Command line mode: python upload_with_metadata.py <pdf_path> <class> <subject>
        pdf_path = sys.argv[1]
        class_num = sys.argv[2]
        subject = sys.argv[3]
        upload_pdf_with_metadata(pdf_path, class_num, subject)
    else:
        # Interactive mode
        interactive_upload()
