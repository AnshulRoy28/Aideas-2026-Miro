#!/usr/bin/env python3
"""Interactive RAG query system."""

import os
import sys
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get configuration from .env
KNOWLEDGE_BASE_ID = os.getenv('KNOWLEDGE_BASE_ID')
MODEL_ID = os.getenv('MODEL_ID', 'amazon.nova-micro-v1:0')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
MAX_RESULTS = int(os.getenv('MAX_RESULTS', '5'))

# Load system prompt from file
def load_system_prompt():
    """Load the system prompt from prompt.txt file."""
    try:
        with open('prompt.txt', 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        print("⚠️  Warning: prompt.txt not found, using default prompt")
        return '''You are a friendly AI tutor for students.

Context: $search_results$
Question: $query$

Provide a clear, concise answer:'''

SYSTEM_PROMPT = load_system_prompt()

# Create Bedrock Agent Runtime client
bedrock_agent = boto3.client(
    'bedrock-agent-runtime',
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

def query_knowledge_base(question):
    """Query the knowledge base with a question and stream the response."""
    try:
        # Query the knowledge base with streaming enabled and system prompt
        response = bedrock_agent.retrieve_and_generate(
            input={
                'text': question
            },
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': KNOWLEDGE_BASE_ID,
                    'modelArn': f'arn:aws:bedrock:{AWS_REGION}::foundation-model/{MODEL_ID}',
                    'retrievalConfiguration': {
                        'vectorSearchConfiguration': {
                            'numberOfResults': MAX_RESULTS
                        }
                    }
                }
            }
        )
        
        # Check if response has streaming
        if 'stream' in response:
            print("\nAnswer:")
            for event in response['stream']:
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        print(chunk['bytes'].decode('utf-8'), end='', flush=True)
            print()  # New line after streaming
        else:
            # Fallback to non-streaming response
            print("\nAnswer:")
            print(response['output']['text'])
        
        # Print citations if available
        print("\n\nSources:")
        
        # Debug: Check what keys are in the response
        # print(f"DEBUG - Response keys: {response.keys()}")
        
        if 'citations' in response and response['citations']:
            for i, citation in enumerate(response['citations'], 1):
                refs = citation.get('retrievedReferences', [])
                if refs:
                    for j, ref in enumerate(refs, 1):
                        # Try different possible location structures
                        location = ref.get('location', {})
                        
                        # Check for S3 location
                        if 's3Location' in location:
                            uri = location['s3Location'].get('uri', 'N/A')
                            print(f"   [{i}.{j}] {uri}")
                        else:
                            # Try to get content or metadata
                            content = ref.get('content', {})
                            metadata = ref.get('metadata', {})
                            if metadata:
                                source = metadata.get('x-amz-bedrock-kb-source-uri', 'Unknown source')
                                print(f"   [{i}.{j}] {source}")
                            elif content:
                                print(f"   [{i}.{j}] Content reference found")
                            else:
                                print(f"   [{i}.{j}] Reference available (structure unknown)")
        elif 'sessionId' in response:
            # Citations might be in a different part of the response
            print("   Session-based response - citations may not be directly available")
        else:
            print("   No source citations available in response")
                    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Make sure your AWS credentials are valid and the Knowledge Base ID is correct.")

if __name__ == "__main__":
    # Check if question was provided as command line argument
    if len(sys.argv) > 1:
        # Use command line argument
        question = ' '.join(sys.argv[1:])
        print(f"\nQuestion: {question}")
        query_knowledge_base(question)
    else:
        # Interactive mode
        print("RAG Query System - Interactive Mode")
        print("Type 'exit' or 'quit' to stop\n")
        
        while True:
            try:
                question = input("Enter your question: ").strip()
                
                if question.lower() in ['exit', 'quit', 'q']:
                    print("Goodbye!")
                    break
                
                if not question:
                    continue
                
                query_knowledge_base(question)
                print("\n" + "-"*50 + "\n")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except EOFError:
                break