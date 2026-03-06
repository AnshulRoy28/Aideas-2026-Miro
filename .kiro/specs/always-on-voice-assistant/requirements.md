# Requirements Document: Always-On Voice Assistant

## Introduction

This document specifies requirements for migrating the Miro student component from an Electron-based GUI application to an always-on, wake-word-activated voice assistant for Raspberry Pi deployment in classroom environments. The system will use local wake word detection and voice activity detection, with cloud-based processing via WebSocket streaming for transcription, knowledge retrieval, and text-to-speech generation.

## Glossary

- **Pi_Client**: Python application running on Raspberry Pi that handles wake word detection, audio capture, and playback
- **Wake_Word_Detector**: Porcupine-based component that listens for the wake word "Miro"
- **VAD**: Voice Activity Detector (Silero-based) that determines when the student has stopped speaking
- **WebSocket_Client**: Component on Pi that maintains bidirectional streaming connection to cloud
- **API_Gateway**: AWS API Gateway WebSocket endpoint that manages connections
- **Voice_Backend**: Fargate-hosted service that orchestrates transcription, retrieval, and generation
- **Transcribe_Stream**: AWS Transcribe streaming service for real-time speech-to-text
- **Knowledge_Base**: AWS Bedrock Knowledge Base containing indexed educational materials
- **Answer_Generator**: AWS Bedrock Claude model that generates grade-appropriate responses
- **TTS_Engine**: AWS Polly service that converts text responses to speech audio
- **IoT_Authenticator**: AWS IoT Core service that validates device certificates
- **Device_Certificate**: X.509 certificate uniquely identifying each classroom Raspberry Pi

## Requirements

### Requirement 1: Wake Word Detection

**User Story:** As a student, I want to activate the assistant by saying "Miro", so that I can ask questions hands-free without pressing buttons.

#### Acceptance Criteria

1. WHEN the Pi_Client starts, THE Wake_Word_Detector SHALL continuously listen for the wake word "Miro"
2. WHEN the wake word "Miro" is detected, THE Wake_Word_Detector SHALL trigger audio capture within 500ms
3. THE Wake_Word_Detector SHALL operate with less than 5% CPU usage on Raspberry Pi 4
4. THE Wake_Word_Detector SHALL achieve at least 95% detection accuracy in quiet environments
5. THE Wake_Word_Detector SHALL reject false positives with at least 98% accuracy
6. WHILE the system is processing a query, THE Wake_Word_Detector SHALL ignore additional wake word detections

### Requirement 2: Voice Activity Detection

**User Story:** As a student, I want the system to know when I've finished speaking, so that I don't have to press a button to submit my question.

#### Acceptance Criteria

1. WHEN the wake word is detected, THE VAD SHALL begin monitoring audio input for speech activity
2. WHILE speech is detected, THE VAD SHALL continue buffering audio data
3. WHEN silence is detected for 1.5 seconds, THE VAD SHALL signal end-of-speech
4. THE VAD SHALL distinguish speech from background classroom noise with at least 90% accuracy
5. THE VAD SHALL operate with less than 10% CPU usage on Raspberry Pi 4
6. IF speech duration exceeds 30 seconds, THEN THE VAD SHALL force end-of-speech and process the captured audio

### Requirement 3: Audio Capture and Buffering

**User Story:** As a student, I want my complete question to be captured clearly, so that the system understands what I'm asking.

#### Acceptance Criteria

1. WHEN wake word is detected, THE Pi_Client SHALL begin capturing audio at 16kHz sample rate
2. THE Pi_Client SHALL buffer audio in 100ms chunks
3. THE Pi_Client SHALL encode audio chunks in PCM format
4. WHEN VAD signals end-of-speech, THE Pi_Client SHALL finalize the audio buffer
5. THE Pi_Client SHALL preserve audio quality with signal-to-noise ratio above 20dB
6. IF audio buffer exceeds 5MB, THEN THE Pi_Client SHALL reject the recording and prompt for shorter input

### Requirement 4: WebSocket Connection Management

**User Story:** As a system administrator, I want reliable connectivity between devices and the cloud, so that students experience minimal disruptions.

#### Acceptance Criteria

1. WHEN Pi_Client starts, THE WebSocket_Client SHALL establish connection to API_Gateway
2. THE WebSocket_Client SHALL authenticate using Device_Certificate before sending data
3. IF connection is lost, THEN THE WebSocket_Client SHALL attempt reconnection with exponential backoff (1s, 2s, 4s, 8s, max 30s)
4. THE WebSocket_Client SHALL maintain heartbeat messages every 30 seconds
5. IF reconnection fails after 5 attempts, THEN THE WebSocket_Client SHALL log error and notify user via audio feedback
6. WHEN connection is established, THE WebSocket_Client SHALL be ready to stream audio within 100ms

### Requirement 5: Audio Streaming to Cloud

**User Story:** As a student, I want my question to be processed quickly, so that I can get answers without long waits.

#### Acceptance Criteria

1. WHEN audio capture begins, THE WebSocket_Client SHALL stream audio chunks to Voice_Backend in real-time
2. THE WebSocket_Client SHALL send chunks with maximum 200ms latency
3. THE WebSocket_Client SHALL include metadata (device_id, timestamp, chunk_sequence) with each chunk
4. IF network latency exceeds 500ms, THEN THE WebSocket_Client SHALL buffer locally and notify user of delay
5. WHEN VAD signals end-of-speech, THE WebSocket_Client SHALL send end-of-stream marker
6. THE WebSocket_Client SHALL compress audio chunks using Opus codec to reduce bandwidth

### Requirement 6: Device Authentication

**User Story:** As a system administrator, I want each device to authenticate securely, so that only authorized classroom devices can access the system.

#### Acceptance Criteria

1. WHEN Pi_Client initializes, THE IoT_Authenticator SHALL validate Device_Certificate
2. THE Device_Certificate SHALL be unique per Raspberry Pi device
3. THE IoT_Authenticator SHALL reject connections with invalid or expired certificates
4. THE Device_Certificate SHALL be stored in read-only filesystem location on Pi
5. THE IoT_Authenticator SHALL support certificate rotation without device reboot
6. IF authentication fails, THEN THE Pi_Client SHALL log error and retry after 60 seconds

### Requirement 7: Cloud Audio Reception

**User Story:** As a backend service, I want to receive complete audio streams, so that I can accurately transcribe student questions.

#### Acceptance Criteria

1. WHEN API_Gateway receives WebSocket connection, THE Voice_Backend SHALL accept the connection
2. THE Voice_Backend SHALL validate device authentication via IoT_Authenticator
3. WHEN audio chunks arrive, THE Voice_Backend SHALL buffer them in sequence order
4. THE Voice_Backend SHALL detect missing chunks using sequence numbers
5. IF chunks arrive out of order, THEN THE Voice_Backend SHALL reorder them before processing
6. WHEN end-of-stream marker is received, THE Voice_Backend SHALL finalize audio buffer and begin transcription

### Requirement 8: Speech-to-Text Transcription

**User Story:** As a student, I want my spoken question to be accurately converted to text, so that the system understands what I'm asking.

#### Acceptance Criteria

1. WHEN audio buffer is finalized, THE Voice_Backend SHALL send audio to Transcribe_Stream
2. THE Transcribe_Stream SHALL return partial transcripts as audio is processed
3. WHEN transcription is complete, THE Transcribe_Stream SHALL return final transcript with confidence scores
4. THE Transcribe_Stream SHALL achieve at least 90% word accuracy for clear speech
5. IF confidence score is below 70%, THEN THE Voice_Backend SHALL request clarification from student
6. THE Transcribe_Stream SHALL support multiple languages (English, Spanish, French, Hindi, Arabic)

### Requirement 9: Knowledge Retrieval

**User Story:** As a student, I want answers based on my study materials, so that I get accurate information relevant to my curriculum.

#### Acceptance Criteria

1. WHEN transcript is received, THE Voice_Backend SHALL query Knowledge_Base with the transcript text
2. THE Knowledge_Base SHALL return top 5 most relevant document chunks
3. THE Knowledge_Base SHALL include relevance scores with each chunk
4. THE Knowledge_Base SHALL return results within 1 second
5. IF no relevant documents are found (relevance score < 0.3), THEN THE Voice_Backend SHALL inform student that the question is outside available materials
6. THE Voice_Backend SHALL include document metadata (title, page number) with retrieved chunks

### Requirement 10: Answer Generation

**User Story:** As a student, I want clear, age-appropriate answers to my questions, so that I can understand the material better.

#### Acceptance Criteria

1. WHEN relevant documents are retrieved, THE Answer_Generator SHALL generate response using transcript and document context
2. THE Answer_Generator SHALL tailor language complexity to student grade level (Class 1-10)
3. THE Answer_Generator SHALL cite source documents in the response
4. THE Answer_Generator SHALL generate responses within 2 seconds
5. THE Answer_Generator SHALL limit responses to 150 words maximum
6. IF the question cannot be answered from available materials, THEN THE Answer_Generator SHALL explain what information is missing

### Requirement 11: Text-to-Speech Synthesis

**User Story:** As a student, I want to hear the answer spoken aloud, so that I can learn through listening.

#### Acceptance Criteria

1. WHEN answer text is generated, THE Voice_Backend SHALL send text to TTS_Engine
2. THE TTS_Engine SHALL synthesize speech using a child-friendly voice
3. THE TTS_Engine SHALL stream audio chunks back to Voice_Backend as they are generated
4. THE TTS_Engine SHALL generate speech at natural speaking rate (150-160 words per minute)
5. THE TTS_Engine SHALL support multiple languages matching the student's query language
6. THE TTS_Engine SHALL include speech marks (phoneme timing) for lip-sync animation

### Requirement 12: Audio Streaming to Device

**User Story:** As a student, I want to hear the answer as soon as possible, so that I don't have to wait for the complete response to be generated.

#### Acceptance Criteria

1. WHEN TTS audio chunks are generated, THE Voice_Backend SHALL stream them to WebSocket_Client immediately
2. THE Voice_Backend SHALL send audio chunks with maximum 100ms latency
3. THE Voice_Backend SHALL include metadata (chunk_sequence, total_chunks) with each audio chunk
4. WHEN all chunks are sent, THE Voice_Backend SHALL send end-of-response marker
5. THE Voice_Backend SHALL compress audio using Opus codec
6. IF streaming fails mid-response, THEN THE Voice_Backend SHALL retry sending remaining chunks

### Requirement 13: Audio Playback

**User Story:** As a student, I want to hear the answer clearly through the speaker, so that I can understand the response.

#### Acceptance Criteria

1. WHEN audio chunks arrive, THE Pi_Client SHALL buffer them in a playback queue
2. THE Pi_Client SHALL begin playback after buffering 500ms of audio
3. THE Pi_Client SHALL play audio at consistent volume level
4. THE Pi_Client SHALL handle chunk arrival jitter without audio glitches
5. WHEN playback completes, THE Pi_Client SHALL return to listening for wake word
6. IF playback buffer underruns, THEN THE Pi_Client SHALL pause and wait for more chunks

### Requirement 14: Error Handling and User Feedback

**User Story:** As a student, I want to know when something goes wrong, so that I understand why I'm not getting an answer.

#### Acceptance Criteria

1. IF wake word detection fails to initialize, THEN THE Pi_Client SHALL play error tone and log diagnostic information
2. IF WebSocket connection cannot be established, THEN THE Pi_Client SHALL play "connection error" audio message
3. IF transcription confidence is too low, THEN THE Voice_Backend SHALL respond with "I didn't understand, please repeat"
4. IF Knowledge_Base query times out, THEN THE Voice_Backend SHALL respond with "I'm having trouble accessing materials, please try again"
5. IF any component fails, THEN THE system SHALL log error details with timestamp and device_id
6. THE Pi_Client SHALL provide audio feedback for state transitions (wake word detected, processing, speaking)

### Requirement 15: Scalability and Concurrency

**User Story:** As a system administrator, I want the system to handle multiple classrooms simultaneously, so that all students can use the assistant at the same time.

#### Acceptance Criteria

1. THE API_Gateway SHALL support at least 100 concurrent WebSocket connections
2. THE Voice_Backend SHALL scale horizontally to handle increased load
3. WHEN load increases, THE Voice_Backend SHALL spawn additional Fargate tasks within 30 seconds
4. THE Voice_Backend SHALL process each student query independently without blocking
5. THE system SHALL maintain response time under 3 seconds even at 80% capacity
6. THE Voice_Backend SHALL implement rate limiting (max 10 queries per minute per device)

### Requirement 16: Audio Format Serialization

**User Story:** As a developer, I want consistent audio format handling, so that audio streams are correctly encoded and decoded across components.

#### Acceptance Criteria

1. THE Pi_Client SHALL serialize audio to PCM 16-bit signed integer format at 16kHz
2. THE WebSocket_Client SHALL encode serialized audio using Opus codec before transmission
3. THE Voice_Backend SHALL decode Opus audio back to PCM format
4. THE TTS_Engine SHALL generate audio in MP3 format
5. THE Voice_Backend SHALL transcode MP3 to Opus before streaming to device
6. FOR ALL audio data, encoding then decoding SHALL preserve intelligibility (PESQ score > 3.5)

### Requirement 17: WebSocket Message Protocol

**User Story:** As a developer, I want a well-defined message protocol, so that client and server can communicate reliably.

#### Acceptance Criteria

1. THE WebSocket_Client SHALL format messages as JSON with fields: message_type, device_id, timestamp, payload
2. THE WebSocket_Client SHALL support message types: audio_chunk, end_of_stream, heartbeat, error
3. THE Voice_Backend SHALL format responses as JSON with fields: message_type, payload, metadata
4. THE Voice_Backend SHALL support message types: audio_chunk, transcript, answer_text, end_of_response, error
5. THE WebSocket protocol SHALL include version field for backward compatibility
6. FOR ALL valid messages, parsing then serializing SHALL produce equivalent message structure (round-trip property)

### Requirement 18: Configuration and Deployment

**User Story:** As a system administrator, I want easy device provisioning, so that I can deploy new classroom devices quickly.

#### Acceptance Criteria

1. THE Pi_Client SHALL read configuration from /etc/miro/config.json
2. THE configuration file SHALL include: api_gateway_url, device_id, certificate_path, audio_settings
3. THE Pi_Client SHALL validate configuration on startup
4. IF configuration is invalid, THEN THE Pi_Client SHALL log specific validation errors and exit
5. THE Pi_Client SHALL support configuration updates without code changes
6. THE system SHALL provide provisioning script that generates Device_Certificate and configuration file

### Requirement 19: Monitoring and Logging

**User Story:** As a system administrator, I want visibility into system health, so that I can troubleshoot issues proactively.

#### Acceptance Criteria

1. THE Pi_Client SHALL log events to /var/log/miro/client.log
2. THE Voice_Backend SHALL emit CloudWatch metrics for: connection_count, query_latency, error_rate
3. THE Voice_Backend SHALL log all errors with stack traces
4. THE system SHALL track end-to-end latency from wake word to audio playback start
5. THE Voice_Backend SHALL alert when error_rate exceeds 5% over 5-minute window
6. THE Pi_Client SHALL include device_id in all log messages

### Requirement 20: Resource Constraints

**User Story:** As a system administrator, I want the Pi client to run efficiently, so that it doesn't overheat or crash on resource-constrained hardware.

#### Acceptance Criteria

1. THE Pi_Client SHALL use less than 30% CPU on average on Raspberry Pi 4
2. THE Pi_Client SHALL use less than 200MB RAM
3. THE Pi_Client SHALL not cause thermal throttling under normal operation
4. THE Pi_Client SHALL release resources properly when idle
5. THE Pi_Client SHALL run continuously for at least 7 days without restart
6. IF memory usage exceeds 250MB, THEN THE Pi_Client SHALL log warning and trigger garbage collection

