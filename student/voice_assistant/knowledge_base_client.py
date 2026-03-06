"""
AWS Bedrock Knowledge Base client for RAG retrieval.
"""
import logging
import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class KnowledgeBaseClient:
    """Client for AWS Bedrock Knowledge Base."""
    
    def __init__(self, region_name="us-east-1"):
        # Load environment variables from .env file
        load_dotenv(dotenv_path='../../.env')
        
        self.region = region_name
        
        # Get credentials from environment
        aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        
        # Create client with explicit credentials
        self.client = boto3.client(
            'bedrock-agent-runtime',
            region_name=region_name,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        self.knowledge_base_id = os.environ.get('KNOWLEDGE_BASE_ID')
        
        if not self.knowledge_base_id:
            raise ValueError("KNOWLEDGE_BASE_ID not configured in .env")
    
    async def query(self, text: str, max_results: int = 3) -> dict:
        """
        Query knowledge base with text.
        
        Args:
            text: Query text
            max_results: Maximum number of results to return
        
        Returns:
            Dict with 'results' (list of chunks) and 'context' (formatted string)
        
        Raises:
            Exception: If query fails
        """
        try:
            logger.info(f"Querying knowledge base: {text}")
            
            response = self.client.retrieve(
                knowledgeBaseId=self.knowledge_base_id,
                retrievalQuery={'text': text},
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': max_results
                    }
                }
            )
            
            # Extract results
            results = []
            for item in response.get('retrievalResults', []):
                content = item.get('content', {}).get('text', '')
                score = item.get('score', 0.0)
                location = item.get('location', {})
                
                # Extract source metadata
                source = "Unknown"
                if location.get('type') == 'S3':
                    s3_location = location.get('s3Location', {})
                    uri = s3_location.get('uri', '')
                    if uri:
                        # Extract filename from S3 URI
                        source = uri.split('/')[-1]
                
                results.append({
                    'content': content,
                    'score': score,
                    'source': source
                })
            
            logger.info(f"Retrieved {len(results)} results from knowledge base")
            
            # Format context for Claude
            context = self._format_context(results)
            
            return {
                'results': results,
                'context': context
            }
        
        except ClientError as e:
            logger.error(f"AWS Bedrock error: {e}")
            raise Exception(f"Knowledge base query error: {e}")
        except Exception as e:
            logger.error(f"Query error: {e}", exc_info=True)
            raise
    
    def _format_context(self, results: list) -> str:
        """Format retrieval results as context string for Claude."""
        if not results:
            return "No relevant information found."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(
                f"[Source {i}: {result['source']}]\n{result['content']}\n"
            )
        
        return "\n".join(context_parts)
