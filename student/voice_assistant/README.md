# Voice Assistant - Hackathon Demo

Web-based voice assistant with spacebar push-to-talk interaction.

## Architecture

**Pipeline:** Browser → WebSocket → Transcribe → Knowledge Base → Claude → Polly → Browser

**Components:**
- `main.py` - FastAPI WebSocket server
- `transcribe_client.py` - AWS Transcribe integration
- `knowledge_base_client.py` - Bedrock Knowledge Base queries
- `answer_generator.py` - Claude answer generation
- `tts_client.py` - AWS Polly text-to-speech
- `pipeline.py` - Orchestrates the complete flow
- `index.html` - Browser frontend

## Setup

### 1. Install Dependencies

```bash
cd student/voice_assistant
pip install -r requirements.txt
```

### 2. Configure Environment

Ensure `.env` in project root contains:

```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_BUCKET_NAME=your_bucket
KNOWLEDGE_BASE_ID=your_kb_id
MODEL_ID=amazon.nova-micro-v1:0
TTS_VOICE_ID=Joanna
TTS_ENGINE=neural
```

### 3. Start Backend

```bash
python main.py
```

Server runs on `http://localhost:8002`

### 4. Open Frontend

Open `index.html` in a browser (Chrome/Edge recommended for best WebRTC support)

## Usage

1. **Allow microphone access** when prompted
2. **Hold SPACEBAR** to record your question
3. **Release SPACEBAR** to send
4. Wait for transcript, answer, and audio response

## Protocol

### Client → Server

```json
{"type": "audio_chunk", "data": "base64_webm_audio"}
{"type": "end_of_stream"}
```

### Server → Client

```json
{"type": "transcript", "text": "transcribed question"}
{"type": "answer", "text": "generated answer with sources"}
{"type": "audio", "data": "base64_mp3_audio"}
{"type": "error", "message": "error description"}
```

## Troubleshooting

**Microphone not working:**
- Check browser permissions
- Use Chrome/Edge (best WebRTC support)
- Ensure HTTPS or localhost

**WebSocket connection fails:**
- Check backend is running on port 8002
- Check firewall settings
- Look for errors in browser console

**Transcription fails:**
- Check S3_BUCKET_NAME is configured
- Verify AWS credentials have Transcribe permissions
- Check CloudWatch logs for errors

**No answer generated:**
- Verify KNOWLEDGE_BASE_ID is correct
- Check Bedrock permissions
- Ensure knowledge base has content

## Performance

- **Transcription:** ~2-3 seconds (batch mode)
- **Knowledge retrieval:** ~0.5-1 second
- **Answer generation:** ~1-2 seconds
- **TTS synthesis:** ~0.5-1 second
- **Total latency:** ~4-7 seconds end-to-end

## Future Enhancements

- Streaming transcription (reduce latency)
- WebRTC audio optimization
- Visual feedback during processing
- Error recovery and retry logic
- Session management
- Authentication
