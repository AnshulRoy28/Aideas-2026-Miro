"""
FastAPI WebSocket server for voice assistant.
Handles bidirectional audio streaming for hackathon demo.
"""
import asyncio
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pipeline import VoicePipeline
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Voice Assistant API")

# CORS for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline
pipeline = VoicePipeline()


@app.get("/")
async def serve_frontend():
    """Serve the voice assistant frontend."""
    return FileResponse("index.html")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "voice-assistant"}


@app.websocket("/voice")
async def voice_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for voice interaction.
    
    Protocol:
    - Client sends: {"type": "audio_chunk", "data": base64_audio}
    - Client sends: {"type": "end_of_stream"}
    - Server sends: {"type": "transcript", "text": "..."}
    - Server sends: {"type": "answer", "text": "..."}
    - Server sends: {"type": "audio", "data": base64_mp3}
    - Server sends: {"type": "error", "message": "..."}
    """
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        audio_chunks = []
        
        while True:
            # Receive message from client
            message = await websocket.receive_json()
            msg_type = message.get("type")
            
            if msg_type == "audio_chunk":
                # Accumulate audio chunks
                audio_data = message.get("data")
                if audio_data:
                    audio_chunks.append(audio_data)
                    logger.debug(f"Received audio chunk ({len(audio_data)} bytes)")
            
            elif msg_type == "end_of_stream":
                logger.info("End of stream received, processing audio")
                
                if not audio_chunks:
                    await websocket.send_json({
                        "type": "error",
                        "message": "No audio data received"
                    })
                    continue
                
                # Process through pipeline
                try:
                    async for response in pipeline.process(audio_chunks):
                        await websocket.send_json(response)
                        logger.info(f"Sent response: {response.get('type')}")
                
                except Exception as e:
                    logger.error(f"Pipeline error: {e}", exc_info=True)
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Processing error: {str(e)}"
                    })
                
                # Reset for next query
                audio_chunks = []
            
            else:
                logger.warning(f"Unknown message type: {msg_type}")
    
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json({
                "type": "error",
                "message": "Internal server error"
            })
        except:
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")
