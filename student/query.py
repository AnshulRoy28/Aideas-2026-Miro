#!/usr/bin/env python3
"""Interactive RAG query system with TTS support."""

import os
import sys
import boto3
import tempfile
from dotenv import load_dotenv

# Try to import playsound for audio playback
try:
    from playsound import playsound
    PLAYSOUND_AVAILABLE = True
except ImportError:
    PLAYSOUND_AVAILABLE = False
    print("⚠️  playsound not installed. TTS will be disabled. Install with: pip install playsound")

# Load environment variables
load_dotenv()

# Get configuration from .env
KNOWLEDGE_BASE_ID = os.getenv('KNOWLEDGE_BASE_ID')
MODEL_ID = os.getenv('MODEL_ID', 'amazon.nova-micro-v1:0')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
MAX_RESULTS = int(os.getenv('MAX_RESULTS', '5'))

# TTS Configuration
ENABLE_TTS = os.getenv('ENABLE_TTS', 'false').lower() == 'true'
TTS_VOICE_ID = os.getenv('TTS_VOICE_ID', 'Joanna')
TTS_ENGINE = os.getenv('TTS_ENGINE', 'neural')
TTS_LANGUAGE_CODE = os.getenv('TTS_LANGUAGE_CODE', 'en-US')

# Load system prompt from file
def load_system_prompt():
    """Load the system prompt from prompt.txt file."""
    try:
        with open('prompt.txt', 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        print("⚠️  Warning: prompt.txt not found, using default prompt")
        return '''You are a friendly AI tutor for students.

Provide a clear, concise answer based on the context below:

{context}

Question: {question}'''

SYSTEM_PROMPT = load_system_prompt()

# Create AWS clients
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

# Language options with voice configurations (using best neural voices)
LANGUAGE_OPTIONS = {
    '1': {'name': 'English (US)', 'voice': 'Ruth', 'code': 'en-US', 'engine': 'generative', 'lang_name': 'English'},
    '2': {'name': 'Hindi', 'voice': 'Kajal', 'code': 'hi-IN', 'engine': 'neural', 'lang_name': 'Hindi'},
    '3': {'name': 'Spanish (Mexico)', 'voice': 'Mia', 'code': 'es-MX', 'engine': 'neural', 'lang_name': 'Spanish'},
    '4': {'name': 'French', 'voice': 'Lea', 'code': 'fr-FR', 'engine': 'neural', 'lang_name': 'French'},
    '5': {'name': 'German', 'voice': 'Vicki', 'code': 'de-DE', 'engine': 'neural', 'lang_name': 'German'},
    '6': {'name': 'Portuguese (Brazil)', 'voice': 'Camila', 'code': 'pt-BR', 'engine': 'neural', 'lang_name': 'Portuguese'},
    '7': {'name': 'Arabic', 'voice': 'Zeina', 'code': 'arb', 'engine': 'neural', 'lang_name': 'Arabic'},
    '8': {'name': 'Chinese (Mandarin)', 'voice': 'Zhiyu', 'code': 'cmn-CN', 'engine': 'neural', 'lang_name': 'Chinese'},
    '9': {'name': 'Japanese', 'voice': 'Kazuha', 'code': 'ja-JP', 'engine': 'neural', 'lang_name': 'Japanese'},
    '10': {'name': 'Korean', 'voice': 'Seoyeon', 'code': 'ko-KR', 'engine': 'neural', 'lang_name': 'Korean'},
}

# Global variable to store selected language
SELECTED_LANGUAGE = None

def select_language():
    """Prompt user to select a language for TTS."""
    global SELECTED_LANGUAGE
    
    if not ENABLE_TTS or not PLAYSOUND_AVAILABLE:
        return None
    
    print("\n🌍 Select your preferred language:")
    print("-" * 40)
    for key, lang in LANGUAGE_OPTIONS.items():
        print(f"  {key}. {lang['name']}")
    print("-" * 40)
    
    while True:
        choice = input("Enter language number (or press Enter to skip TTS): ").strip()
        
        if not choice:
            print("TTS disabled for this session.\n")
            return None
        
        if choice in LANGUAGE_OPTIONS:
            SELECTED_LANGUAGE = LANGUAGE_OPTIONS[choice]
            print(f"✓ Selected: {SELECTED_LANGUAGE['name']} (Voice: {SELECTED_LANGUAGE['voice']})\n")
            return SELECTED_LANGUAGE
        else:
            print("Invalid choice. Please try again.")

def text_to_speech(text, voice_id=None, language_code=None, engine=None):
    """Convert text to speech using AWS Polly and play it."""
    if not ENABLE_TTS or not PLAYSOUND_AVAILABLE or not SELECTED_LANGUAGE:
        return
    
    try:
        # Use selected language settings
        voice = voice_id or SELECTED_LANGUAGE['voice']
        lang = language_code or SELECTED_LANGUAGE['code']
        tts_engine = engine or SELECTED_LANGUAGE.get('engine', 'neural')
        
        # Generate speech using Polly
        response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId=voice,
            Engine=tts_engine,
            LanguageCode=lang
        )
        
        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
            temp_audio.write(response['AudioStream'].read())
            temp_audio_path = temp_audio.name
        
        # Play audio using playsound
        playsound(temp_audio_path)
        
        # Clean up temporary file
        os.unlink(temp_audio_path)
        
    except Exception as e:
        print(f"⚠️  TTS Error: {str(e)}")

def query_knowledge_base(question):
    """Query the knowledge base using retrieve API and generate response."""
    try:
        # Step 1: Retrieve relevant documents from knowledge base
        retrieve_response = bedrock_agent.retrieve(
            knowledgeBaseId=KNOWLEDGE_BASE_ID,
            retrievalQuery={
                'text': question
            },
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': MAX_RESULTS
                }
            }
        )
        
        # Step 2: Extract retrieved documents
        retrieved_docs = retrieve_response.get('retrievalResults', [])
        
        if not retrieved_docs:
            answer_text = "I don't have any information about that in my study materials. Please ask me something from your textbooks!"
            print(f"\nAnswer:\n{answer_text}")
            if ENABLE_TTS:
                text_to_speech(answer_text)
            return
        
        # Step 3: Build context from retrieved documents
        context = "\n\n".join([
            f"Document {i+1}:\n{doc['content']['text']}"
            for i, doc in enumerate(retrieved_docs)
        ])
        
        # Step 4: Format the prompt with context and question
        # Add language instruction if a non-English language is selected
        language_instruction = ""
        if SELECTED_LANGUAGE and SELECTED_LANGUAGE['lang_name'] != 'English':
            language_instruction = f"\n\nIMPORTANT: You MUST respond in {SELECTED_LANGUAGE['lang_name']} language. Translate your entire answer to {SELECTED_LANGUAGE['lang_name']}."
        
        formatted_prompt = SYSTEM_PROMPT.replace('{context}', context).replace('{question}', question) + language_instruction
        
        # Step 5: Generate response using Bedrock Runtime with streaming
        response = bedrock_runtime.converse_stream(
            modelId=MODEL_ID,
            messages=[
                {
                    'role': 'user',
                    'content': [{'text': formatted_prompt}]
                }
            ],
            inferenceConfig={
                'maxTokens': 500,
                'temperature': 0.3,
                'topP': 0.9
            }
        )
        
        # Step 6: Stream the response and collect full text for TTS
        print("\nAnswer:")
        full_answer = ""
        stream = response.get('stream')
        if stream:
            for event in stream:
                if 'contentBlockDelta' in event:
                    delta = event['contentBlockDelta']['delta']
                    if 'text' in delta:
                        text_chunk = delta['text']
                        print(text_chunk, end='', flush=True)
                        full_answer += text_chunk
        print()  # New line after streaming
        
        # Step 7: Play TTS if enabled
        if ENABLE_TTS and SELECTED_LANGUAGE and full_answer:
            print("\n🔊 Playing audio...")
            text_to_speech(full_answer)
        
        # Step 8: Display sources
        print("\n\nSources:")
        for i, doc in enumerate(retrieved_docs, 1):
            location = doc.get('location', {})
            if 's3Location' in location:
                uri = location['s3Location'].get('uri', 'N/A')
                print(f"   [{i}] {uri}")
            else:
                metadata = doc.get('metadata', {})
                if metadata:
                    source = metadata.get('x-amz-bedrock-kb-source-uri', f'Document {i}')
                    print(f"   [{i}] {source}")
                    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Make sure your AWS credentials are valid and the Knowledge Base ID is correct.")

if __name__ == "__main__":
    # Display welcome message
    print("=" * 50)
    print("  Welcome to Miro - Your AI Learning Companion")
    print("=" * 50)
    
    # Select language for TTS
    if ENABLE_TTS and PLAYSOUND_AVAILABLE:
        select_language()
    elif ENABLE_TTS and not PLAYSOUND_AVAILABLE:
        print("⚠️  TTS disabled: playsound not installed\n")
    
    # Check if question was provided as command line argument
    if len(sys.argv) > 1:
        # Use command line argument
        question = ' '.join(sys.argv[1:])
        print(f"\nQuestion: {question}")
        query_knowledge_base(question)
    else:
        # Interactive mode
        print("Interactive Mode - Type 'exit' or 'quit' to stop\n")
        
        while True:
            try:
                question = input("Enter your question: ").strip()
                
                if question.lower() in ['exit', 'quit', 'q']:
                    print("\nThank you for using Miro! Goodbye! 👋")
                    break
                
                if not question:
                    continue
                
                query_knowledge_base(question)
                print("\n" + "-"*50 + "\n")
                
            except KeyboardInterrupt:
                print("\n\nThank you for using Miro! Goodbye! 👋")
                break
            except EOFError:
                break