#!/usr/bin/env python3
"""
Miro Student Backend Server
FastAPI server for RAG queries - integrates with existing query.py logic
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import boto3
from dotenv import load_dotenv
import os
import sys
import io

# Load environment variables
load_dotenv()
if not os.getenv('KNOWLEDGE_BASE_ID'):
    parent_env = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(parent_env):
        load_dotenv(parent_env)

# Configuration
KNOWLEDGE_BASE_ID = os.getenv('KNOWLEDGE_BASE_ID')
MODEL_ID = os.getenv('MODEL_ID', 'amazon.nova-micro-v1:0')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
MAX_RESULTS = int(os.getenv('MAX_RESULTS', '5'))

# Initialize FastAPI
app = FastAPI(title="Miro Student API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AWS Clients
bedrock_agent = boto3.client(
    'bedrock-agent-runtime',
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

bedrock_runtime = boto3.client(
    'bedrock-runtime',
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

polly_client = boto3.client(
    'polly',
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

# Load system prompt
def load_system_prompt():
    """Load the system prompt from prompt.txt file."""
    try:
        prompt_paths = ['prompt.txt', os.path.join(os.path.dirname(__file__), 'prompt.txt')]
        for path in prompt_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
        raise FileNotFoundError
    except FileNotFoundError:
        return '''You are a friendly AI tutor for students.

Provide a clear, concise answer based on the context below:

{context}

Question: {question}'''

SYSTEM_PROMPT = load_system_prompt()

# Request/Response Models
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[str]

class TTSRequest(BaseModel):
    text: str
    voice_id: str = "Ruth"  # Default to Ruth (generative - natural sound)

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "Miro Student API"}

@app.post("/api/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Process a student query using RAG."""
    try:
        # Step 1: Retrieve relevant documents
        retrieve_response = bedrock_agent.retrieve(
            knowledgeBaseId=KNOWLEDGE_BASE_ID,
            retrievalQuery={'text': request.question},
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': MAX_RESULTS
                }
            }
        )
        
        retrieved_docs = retrieve_response.get('retrievalResults', [])
        
        if not retrieved_docs:
            return QueryResponse(
                answer="I don't have any information about that in my study materials. Please ask me something from your textbooks!",
                sources=[]
            )
        
        # Step 2: Build context
        context = "\n\n".join([
            f"Document {i+1}:\n{doc['content']['text']}"
            for i, doc in enumerate(retrieved_docs)
        ])
        
        # Step 3: Generate response
        formatted_prompt = SYSTEM_PROMPT.replace('{context}', context).replace('{question}', request.question)
        
        response = bedrock_runtime.converse(
            modelId=MODEL_ID,
            messages=[{
                'role': 'user',
                'content': [{'text': formatted_prompt}]
            }],
            inferenceConfig={
                'maxTokens': 500,
                'temperature': 0.3,
                'topP': 0.9
            }
        )
        
        # Extract answer
        answer = response['output']['message']['content'][0]['text']
        
        # Extract sources
        sources = []
        for doc in retrieved_docs:
            location = doc.get('location', {})
            if 's3Location' in location:
                uri = location['s3Location'].get('uri', '')
                if uri:
                    sources.append(uri)
        
        return QueryResponse(answer=answer, sources=sources)
        
    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech using AWS Polly."""
    try:
        # Determine engine based on voice
        engine = 'generative' if request.voice_id == 'Ruth' else 'neural'
        
        # Generate speech using Polly
        response = polly_client.synthesize_speech(
            Text=request.text,
            OutputFormat='mp3',
            VoiceId=request.voice_id,
            Engine=engine,
            LanguageCode='en-US'
        )
        
        # Read audio stream
        audio_stream = response['AudioStream'].read()
        
        # Return audio as streaming response
        return StreamingResponse(
            io.BytesIO(audio_stream),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3"
            }
        )
        
    except Exception as e:
        print(f"Error generating speech: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
