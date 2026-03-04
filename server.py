#!/usr/bin/env python3
"""FastAPI server for S3 document management."""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import boto3
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from typing import List, Dict, Any
import time

# Load environment variables
load_dotenv()

# Configuration
BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'my-nova-rag-data')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
ACCESS_KEY_ID = os.getenv('BEDROCK_UPLOAD_ACCESS_KEY_ID')
SECRET_ACCESS_KEY = os.getenv('BEDROCK_UPLOAD_SECRET_ACCESS_KEY')
KNOWLEDGE_BASE_ID = os.getenv('KNOWLEDGE_BASE_ID')
DATA_SOURCE_ID = os.getenv('DATA_SOURCE_ID')  # New: Data source ID

# Initialize FastAPI app
app = FastAPI(title="Miro API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize S3 client
s3_client = boto3.client(
    's3',
    region_name=AWS_REGION,
    aws_access_key_id=ACCESS_KEY_ID,
    aws_secret_access_key=SECRET_ACCESS_KEY
)

# Initialize Bedrock Agent client for Knowledge Base sync
bedrock_agent_client = boto3.client(
    'bedrock-agent',
    region_name=AWS_REGION,
    aws_access_key_id=ACCESS_KEY_ID,
    aws_secret_access_key=SECRET_ACCESS_KEY
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Miro API", "version": "1.0.0"}

def trigger_knowledge_base_sync():
    """Trigger Knowledge Base data source sync/ingestion."""
    if not KNOWLEDGE_BASE_ID or not DATA_SOURCE_ID:
        print("⚠️  Warning: KNOWLEDGE_BASE_ID or DATA_SOURCE_ID not configured. Skipping sync.")
        return None
    
    try:
        print(f"🔄 Triggering Knowledge Base sync...")
        response = bedrock_agent_client.start_ingestion_job(
            knowledgeBaseId=KNOWLEDGE_BASE_ID,
            dataSourceId=DATA_SOURCE_ID,
            description="Auto-sync after document upload"
        )
        
        ingestion_job_id = response['ingestionJob']['ingestionJobId']
        print(f"✅ Sync job started: {ingestion_job_id}")
        return ingestion_job_id
        
    except Exception as e:
        print(f"❌ Error triggering sync: {e}")
        return None

def check_ingestion_status(ingestion_job_id):
    """Check the status of an ingestion job."""
    try:
        response = bedrock_agent_client.get_ingestion_job(
            knowledgeBaseId=KNOWLEDGE_BASE_ID,
            dataSourceId=DATA_SOURCE_ID,
            ingestionJobId=ingestion_job_id
        )
        return response['ingestionJob']['status']
    except Exception as e:
        print(f"Error checking ingestion status: {e}")
        return None

@app.post("/api/sync-knowledge-base")
async def sync_knowledge_base():
    """Manually trigger Knowledge Base sync."""
    if not KNOWLEDGE_BASE_ID or not DATA_SOURCE_ID:
        raise HTTPException(
            status_code=400, 
            detail="Knowledge Base ID or Data Source ID not configured"
        )
    
    try:
        ingestion_job_id = trigger_knowledge_base_sync()
        
        if not ingestion_job_id:
            raise HTTPException(status_code=500, detail="Failed to start sync job")
        
        return {
            "message": "Knowledge Base sync started",
            "ingestion_job_id": ingestion_job_id,
            "status": "STARTING"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sync-status/{ingestion_job_id}")
async def get_sync_status(ingestion_job_id: str):
    """Get the status of a Knowledge Base sync job."""
    if not KNOWLEDGE_BASE_ID or not DATA_SOURCE_ID:
        raise HTTPException(
            status_code=400, 
            detail="Knowledge Base ID or Data Source ID not configured"
        )
    
    try:
        status = check_ingestion_status(ingestion_job_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Ingestion job not found")
        
        return {
            "ingestion_job_id": ingestion_job_id,
            "status": status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents")
async def list_documents():
    """List all PDF documents in the S3 bucket with their metadata."""
    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        
        if 'Contents' not in response:
            return {"documents": [], "count": 0, "classes": [], "subjects": []}
        
        # Filter only PDF files
        pdf_files = [obj for obj in response['Contents'] if obj['Key'].endswith('.pdf')]
        
        documents = []
        classes_set = set()
        subjects_set = set()
        
        for obj in pdf_files:
            # Get metadata for each file
            metadata_response = s3_client.head_object(Bucket=BUCKET_NAME, Key=obj['Key'])
            
            # Try to get the metadata.json file
            metadata_attrs = {}
            try:
                metadata_key = f"{obj['Key']}.metadata.json"
                metadata_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=metadata_key)
                metadata_content = metadata_obj['Body'].read().decode('utf-8')
                import json
                metadata_json = json.loads(metadata_content)
                metadata_attrs = metadata_json.get('metadataAttributes', {})
                
                # Collect unique classes and subjects
                if 'class' in metadata_attrs:
                    classes_set.add(metadata_attrs['class'])
                if 'subject' in metadata_attrs:
                    subjects_set.add(metadata_attrs['subject'])
            except:
                pass
            
            doc = {
                "key": obj['Key'],
                "size": obj['Size'],
                "lastModified": obj['LastModified'].isoformat(),
                "etag": obj['ETag'].strip('"'),
                "contentType": metadata_response.get('ContentType', 'application/pdf'),
                "storageClass": obj.get('StorageClass', 'STANDARD'),
                "metadata": metadata_response.get('Metadata', {}),
                "encryption": metadata_response.get('ServerSideEncryption', None),
                "class": metadata_attrs.get('class', 'Unclassified'),
                "subject": metadata_attrs.get('subject', 'General')
            }
            documents.append(doc)
        
        # Sort classes and subjects
        classes_list = sorted(list(classes_set), key=lambda x: int(x) if x.isdigit() else 999)
        subjects_list = sorted(list(subjects_set))
        
        return {
            "documents": documents,
            "count": len(documents),
            "classes": classes_list,
            "subjects": subjects_list
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents/{file_key:path}")
async def get_document_metadata(file_key: str):
    """Get metadata for a specific document."""
    try:
        response = s3_client.head_object(Bucket=BUCKET_NAME, Key=file_key)
        
        return {
            "key": file_key,
            "contentType": response.get('ContentType'),
            "contentLength": response.get('ContentLength'),
            "lastModified": response.get('LastModified').isoformat(),
            "etag": response.get('ETag', '').strip('"'),
            "metadata": response.get('Metadata', {}),
            "encryption": response.get('ServerSideEncryption'),
            "storageClass": response.get('StorageClass', 'STANDARD')
        }
        
    except s3_client.exceptions.NoSuchKey:
        raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents/{file_key:path}/download-url")
async def get_download_url(file_key: str, expires: int = 3600):
    """Generate a presigned URL for downloading a document."""
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': file_key},
            ExpiresIn=expires
        )
        
        return {
            "url": url,
            "expires_in": expires,
            "key": file_key
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metadata/{file_key:path}")
async def get_metadata_json(file_key: str):
    """Get the contents of a .metadata.json file."""
    try:
        # Ensure we're looking for the metadata file
        if not file_key.endswith('.metadata.json'):
            metadata_key = f"{file_key}.metadata.json"
        else:
            metadata_key = file_key
        
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=metadata_key)
        content = response['Body'].read().decode('utf-8')
        
        import json
        metadata = json.loads(content)
        
        return {
            "key": metadata_key,
            "content": metadata
        }
        
    except s3_client.exceptions.NoSuchKey:
        raise HTTPException(status_code=404, detail="Metadata file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/documents/{file_key:path}")
async def delete_document(file_key: str):
    """Delete a document and its metadata from S3."""
    try:
        # Delete the main PDF file
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=file_key)
        
        # Try to delete the associated metadata.json file if it exists
        try:
            metadata_key = f"{file_key}.metadata.json"
            s3_client.delete_object(Bucket=BUCKET_NAME, Key=metadata_key)
        except:
            pass  # Metadata file might not exist
        
        return {
            "message": "Document deleted successfully",
            "key": file_key
        }
        
    except s3_client.exceptions.NoSuchKey:
        raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents/{file_key:path}/exists")
async def check_document_exists(file_key: str):
    """Check if a document exists in S3."""
    try:
        s3_client.head_object(Bucket=BUCKET_NAME, Key=file_key)
        return {"exists": True, "key": file_key}
    except s3_client.exceptions.ClientError:
        return {"exists": False, "key": file_key}

@app.put("/api/documents/{file_key:path}/rename")
async def rename_document(file_key: str, new_name: str):
    """Rename a document (keeps metadata with the file)."""
    try:
        # Validate new name
        if not new_name.endswith('.pdf'):
            new_name += '.pdf'
        
        # Check if new name already exists
        try:
            s3_client.head_object(Bucket=BUCKET_NAME, Key=new_name)
            raise HTTPException(status_code=400, detail="A file with this name already exists")
        except s3_client.exceptions.ClientError:
            pass  # Good, file doesn't exist
        
        # Copy the PDF to new name
        s3_client.copy_object(
            Bucket=BUCKET_NAME,
            CopySource={'Bucket': BUCKET_NAME, 'Key': file_key},
            Key=new_name
        )
        
        # Copy the metadata.json if it exists
        try:
            old_metadata_key = f"{file_key}.metadata.json"
            new_metadata_key = f"{new_name}.metadata.json"
            s3_client.copy_object(
                Bucket=BUCKET_NAME,
                CopySource={'Bucket': BUCKET_NAME, 'Key': old_metadata_key},
                Key=new_metadata_key
            )
        except:
            pass  # Metadata file might not exist
        
        # Delete old files
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=file_key)
        try:
            s3_client.delete_object(Bucket=BUCKET_NAME, Key=f"{file_key}.metadata.json")
        except:
            pass
        
        return {
            "message": "Document renamed successfully",
            "old_key": file_key,
            "new_key": new_name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/documents/{file_key:path}/replace")
async def replace_document(file_key: str):
    """Replace document content (for file upload - placeholder for now)."""
    # This endpoint will be used when we add file upload functionality
    raise HTTPException(status_code=501, detail="File upload not yet implemented. Use the Python script for now.")

@app.post("/api/upload")
async def upload_document(
    file: UploadFile = File(...),
    class_num: str = Form(...),
    subject: str = Form(...)
):
    """Upload a PDF document with metadata to S3."""
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Check if file already exists
        try:
            s3_client.head_object(Bucket=BUCKET_NAME, Key=file.filename)
            raise HTTPException(status_code=409, detail=f"A file with the name '{file.filename}' already exists")
        except s3_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] != '404':
                raise
        
        # Read file content
        file_content = await file.read()
        
        # Upload PDF to S3
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=file.filename,
            Body=file_content,
            ContentType='application/pdf'
        )
        
        # Create and upload metadata
        metadata = {
            "metadataAttributes": {
                "class": class_num,
                "subject": subject
            }
        }
        
        metadata_key = f"{file.filename}.metadata.json"
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=metadata_key,
            Body=json.dumps(metadata),
            ContentType='application/json'
        )
        
        return {
            "message": "Document uploaded successfully",
            "filename": file.filename,
            "class": class_num,
            "subject": subject,
            "size": len(file_content),
            "sync_triggered": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Trigger Knowledge Base sync in background (non-blocking)
        try:
            if KNOWLEDGE_BASE_ID and DATA_SOURCE_ID:
                trigger_knowledge_base_sync()
        except:
            pass  # Don't fail upload if sync fails

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test S3 connection
        s3_client.head_bucket(Bucket=BUCKET_NAME)
        return {"status": "healthy", "s3_connection": "ok"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
