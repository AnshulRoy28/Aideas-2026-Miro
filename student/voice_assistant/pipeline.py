"""
Voice processing pipeline orchestrator.
Coordinates: Transcribe → Knowledge Base → Claude → Polly
"""
import logging
from typing import AsyncGenerator
from transcribe_client import TranscribeClient
from knowledge_base_client import KnowledgeBaseClient
from answer_generator import AnswerGenerator
from tts_client import TTSClient

logger = logging.getLogger(__name__)


class VoicePipeline:
    """Orchestrates the voice assistant processing pipeline."""
    
    def __init__(self):
        self.transcribe = TranscribeClient()
        self.knowledge_base = KnowledgeBaseClient()
        self.answer_gen = AnswerGenerator()
        self.tts = TTSClient()
    
    async def process(self, audio_chunks: list) -> AsyncGenerator[dict, None]:
        """
        Process audio through the complete pipeline.
        
        Args:
            audio_chunks: List of base64-encoded audio data
        
        Yields:
            Response messages:
            - {"type": "transcript", "text": "..."}
            - {"type": "answer", "text": "..."}
            - {"type": "audio", "data": "base64_mp3"}
            - {"type": "error", "message": "..."}
        """
        try:
            # Step 1: Transcribe audio
            logger.info("Pipeline: Starting transcription")
            transcript = await self.transcribe.transcribe_audio(audio_chunks)
            
            if not transcript or not transcript.strip():
                yield {
                    "type": "error",
                    "message": "Could not understand audio. Please try again."
                }
                return
            
            yield {
                "type": "transcript",
                "text": transcript
            }
            
            # Step 2: Query knowledge base
            logger.info("Pipeline: Querying knowledge base")
            kb_result = await self.knowledge_base.query(transcript, max_results=3)
            
            if not kb_result['results']:
                yield {
                    "type": "answer",
                    "text": "I couldn't find relevant information in the course materials for that question."
                }
                return
            
            # Step 3: Generate answer with Claude
            logger.info("Pipeline: Generating answer")
            answer_result = await self.answer_gen.generate_answer(
                question=transcript,
                context=kb_result['context'],
                sources=kb_result['results']
            )
            
            answer_text = answer_result['answer']
            sources = answer_result['sources']
            
            # Add source citations
            if sources:
                answer_with_sources = f"{answer_text}\n\nSources: {', '.join(sources)}"
            else:
                answer_with_sources = answer_text
            
            yield {
                "type": "answer",
                "text": answer_with_sources
            }
            
            # Step 4: Synthesize speech
            logger.info("Pipeline: Synthesizing speech")
            audio_data = await self.tts.synthesize(answer_text)
            
            yield {
                "type": "audio",
                "data": audio_data
            }
            
            logger.info("Pipeline: Complete")
        
        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
            yield {
                "type": "error",
                "message": f"Sorry, something went wrong: {str(e)}"
            }
