"""
AWS Polly TTS client for text-to-speech synthesis.
"""
import base64
import logging
import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class TTSClient:
    """Client for AWS Polly text-to-speech."""
    
    def __init__(self, region_name="us-east-1"):
        # Load environment variables from .env file
        load_dotenv(dotenv_path='../../.env')
        
        self.region = region_name
        
        # Get credentials from environment
        aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        
        # Create client with explicit credentials
        self.client = boto3.client(
            'polly',
            region_name=region_name,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        self.voice_id = os.environ.get('TTS_VOICE_ID', 'Joanna')
        self.engine = os.environ.get('TTS_ENGINE', 'neural')
    
    async def synthesize(self, text: str) -> str:
        """
        Synthesize speech from text.
        
        Args:
            text: Text to synthesize
        
        Returns:
            Base64-encoded MP3 audio data
        
        Raises:
            Exception: If synthesis fails
        """
        try:
            logger.info(f"Synthesizing speech ({len(text)} chars)")
            
            response = self.client.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=self.voice_id,
                Engine=self.engine
            )
            
            # Read audio stream
            audio_data = response['AudioStream'].read()
            logger.info(f"Synthesized {len(audio_data)} bytes of audio")
            
            # Encode as base64 for JSON transmission
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            return audio_base64
        
        except ClientError as e:
            logger.error(f"AWS Polly error: {e}")
            raise Exception(f"TTS synthesis error: {e}")
        except Exception as e:
            logger.error(f"Synthesis error: {e}", exc_info=True)
            raise
