"""
Amazon Nova answer generator via AWS Bedrock.
"""
import json
import logging
import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class AnswerGenerator:
    """Generate answers using Amazon Nova via Bedrock."""
    
    def __init__(self, region_name="us-east-1"):
        # Load environment variables from .env file
        load_dotenv(dotenv_path='../../.env')
        
        self.region = region_name
        
        # Get credentials from environment
        aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        
        # Create client with explicit credentials
        self.client = boto3.client(
            'bedrock-runtime',
            region_name=region_name,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        self.model_id = os.environ.get('MODEL_ID', 'amazon.nova-micro-v1:0')
    
    async def generate_answer(self, question: str, context: str, sources: list) -> dict:
        """
        Generate answer using Amazon Nova with retrieved context.
        
        Args:
            question: User's question
            context: Retrieved context from knowledge base
            sources: List of source documents
        
        Returns:
            Dict with 'answer' (text) and 'sources' (list)
        
        Raises:
            Exception: If generation fails
        """
        try:
            logger.info(f"Generating answer for: {question}")
            
            # Build prompt
            prompt = self._build_prompt(question, context)
            
            # Call Nova with correct API format
            request_body = {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ],
                "inferenceConfig": {
                    "max_new_tokens": 150,  # ~75 words for concise answers
                    "temperature": 0.7
                }
            }
            
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            # Parse Nova response format
            response_body = json.loads(response['body'].read())
            answer_text = response_body['output']['message']['content'][0]['text']
            
            logger.info(f"Generated answer ({len(answer_text)} chars)")
            
            # Format sources for citation
            source_list = [s['source'] for s in sources if s.get('source')]
            
            return {
                'answer': answer_text,
                'sources': source_list
            }
        
        except ClientError as e:
            logger.error(f"AWS Bedrock error: {e}")
            raise Exception(f"Answer generation error: {e}")
        except Exception as e:
            logger.error(f"Generation error: {e}", exc_info=True)
            raise
    
    def _build_prompt(self, question: str, context: str) -> str:
        """Build prompt for Amazon Nova."""
        return f"""Answer the student's question using the provided context. Be direct and concise.

Context:
{context}

Question: {question}

Instructions:
- Answer in 2-3 sentences maximum
- No emojis or filler phrases
- No encouragement or pleasantries
- Just the core information
- If context doesn't have the answer, say "I don't have that information"

Answer:"""
