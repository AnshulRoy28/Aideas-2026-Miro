"""
AWS Transcribe Streaming client for real-time speech-to-text.
"""
import asyncio
import base64
import logging
from io import BytesIO
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import os
logger = logging.getLogger(__name__)


class TranscribeClient:
    """Client for AWS Transcribe Streaming."""
    
    def __init__(self, region_name="us-east-1"):
        # Load environment variables from .env file
        load_dotenv(dotenv_path='../../.env')
        
        self.region = region_name
        
        # Get credentials from environment
        aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        
        # Create client with explicit credentials
        self.client = boto3.client(
            'transcribe',
            region_name=region_name,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
    
    async def transcribe_audio(self, audio_chunks: list) -> str:
        """
        Transcribe audio chunks to text.
        
        Args:
            audio_chunks: List of base64-encoded audio data
        
        Returns:
            Transcript text
        
        Raises:
            Exception: If transcription fails
        """
        try:
            # Combine audio chunks
            audio_data = b''.join([base64.b64decode(chunk) for chunk in audio_chunks])
            logger.info(f"Transcribing {len(audio_data)} bytes of audio")
            
            # For hackathon demo, use synchronous transcription via S3
            # (Streaming transcription requires more complex async setup)
            import tempfile
            import os
            from botocore.config import Config
            
            # Get credentials for S3 client
            aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
            aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
            
            # Upload to S3 temporarily
            s3_client = boto3.client(
                's3',
                region_name=self.region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key
            )
            bucket = os.environ.get('S3_BUCKET_NAME')
            
            if not bucket:
                raise ValueError("S3_BUCKET_NAME not configured")
            
            # Create temp file
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as tmp:
                tmp.write(audio_data)
                tmp_path = tmp.name
            
            try:
                # Upload to S3
                import uuid
                key = f"voice-assistant/audio-{uuid.uuid4()}.webm"
                s3_client.upload_file(tmp_path, bucket, key)
                logger.info(f"Uploaded audio to s3://{bucket}/{key}")
                
                # Start transcription job
                job_name = f"voice-{uuid.uuid4()}"
                self.client.start_transcription_job(
                    TranscriptionJobName=job_name,
                    Media={'MediaFileUri': f's3://{bucket}/{key}'},
                    MediaFormat='webm',
                    LanguageCode='en-US'
                )
                
                # Poll for completion (max 30 seconds)
                max_attempts = 30
                for attempt in range(max_attempts):
                    await asyncio.sleep(1)
                    
                    response = self.client.get_transcription_job(
                        TranscriptionJobName=job_name
                    )
                    status = response['TranscriptionJob']['TranscriptionJobStatus']
                    
                    if status == 'COMPLETED':
                        # Get transcript
                        transcript_uri = response['TranscriptionJob']['Transcript']['TranscriptFileUri']
                        
                        # Download transcript
                        import requests
                        transcript_response = requests.get(transcript_uri)
                        transcript_data = transcript_response.json()
                        
                        transcript_text = transcript_data['results']['transcripts'][0]['transcript']
                        logger.info(f"Transcription complete: {transcript_text}")
                        
                        # Cleanup
                        self.client.delete_transcription_job(TranscriptionJobName=job_name)
                        s3_client.delete_object(Bucket=bucket, Key=key)
                        
                        return transcript_text
                    
                    elif status == 'FAILED':
                        error = response['TranscriptionJob'].get('FailureReason', 'Unknown error')
                        raise Exception(f"Transcription failed: {error}")
                
                raise Exception("Transcription timeout")
            
            finally:
                # Cleanup temp file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        
        except ClientError as e:
            logger.error(f"AWS Transcribe error: {e}")
            raise Exception(f"Transcription service error: {e}")
        except Exception as e:
            logger.error(f"Transcription error: {e}", exc_info=True)
            raise
