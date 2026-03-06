# Implementation Plan: Always-On Voice Assistant

## Overview

This implementation plan transforms the Miro student component from an Electron-based GUI to a headless, wake-word-activated voice assistant for Raspberry Pi deployment. The system consists of two main components:

1. **Pi_Client**: Python application running on Raspberry Pi handling wake word detection (Porcupine), voice activity detection (Silero VAD), audio capture/playback, and WebSocket communication.

2. **Voice_Backend**: Python FastAPI service on AWS Fargate orchestrating AWS Transcribe Streaming (STT), AWS Bedrock Knowledge Base (RAG), AWS Bedrock Claude (answer generation), and AWS Polly (TTS).

The implementation follows an incremental approach, building and testing each component independently before integration. All code will be implemented in Python using the libraries specified in the design document.

## Tasks

- [ ] 1. Set up Pi Client project structure and dependencies
  - Create student/pi_client/ directory structure
  - Create requirements.txt with dependencies: pvporcupine, torch (Silero VAD), pyaudio, websockets, numpy, scipy, opuslib
  - Create main.py entry point with argument parsing
  - Create config.example.json template
  - Set up Python logging configuration
  - _Requirements: 18.1, 18.2, 19.1_

- [ ] 2. Implement Configuration Manager
  - [ ] 2.1 Create config_manager.py module
    - Implement ConfigManager class with JSON loading
    - Add schema validation for required fields (api_gateway_url, device_id, certificate_path, audio_settings)
    - Support environment variable overrides
    - Provide default values for optional fields
    - _Requirements: 18.1, 18.2, 18.3, 18.5_

  - [ ]* 2.2 Write property test for configuration validation
    - **Property 64: Configuration Schema Validation**
    - **Property 65: Configuration Startup Validation**
    - **Property 66: Configuration Update Without Code Changes**
    - **Validates: Requirements 18.2, 18.3, 18.5**


- [ ] 3. Implement Audio Capture System
  - [ ] 3.1 Create audio_capture.py module
    - Implement AudioCapture class using PyAudio
    - Configure for 16kHz sample rate, 16-bit depth, mono channel
    - Implement 100ms chunk buffering (1600 samples)
    - Add ring buffer for pre-wake-word audio (500ms)
    - _Requirements: 3.1, 3.2, 3.3_

  - [ ]* 3.2 Write property test for audio capture format
    - **Property 10: Audio Capture Format**
    - **Property 11: Audio Quality Preservation**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.5, 16.1**

- [ ] 4. Implement Audio Playback System
  - [ ] 4.1 Create audio_playback.py module
    - Implement AudioPlayback class using PyAudio
    - Add playback queue with 500ms minimum buffer
    - Implement jitter handling for smooth playback
    - Add volume control and consistency
    - _Requirements: 13.1, 13.2, 13.3, 13.4_

  - [ ]* 4.2 Write property tests for audio playback
    - **Property 44: Audio Playback Buffering**
    - **Property 45: Playback Start Delay**
    - **Property 46: Playback Volume Consistency**
    - **Property 47: Playback Jitter Handling**
    - **Validates: Requirements 13.1, 13.2, 13.3, 13.4**

- [ ] 5. Implement Wake Word Detector
  - [ ] 5.1 Create wake_word_detector.py module
    - Integrate Porcupine Python SDK (pvporcupine)
    - Load custom "Miro" wake word model
    - Process audio in 512-sample frames (32ms at 16kHz)
    - Run detection in dedicated thread
    - Add callback registration for wake word events
    - _Requirements: 1.1, 1.2_

  - [ ]* 5.2 Write property tests for wake word detection
    - **Property 1: Wake Word Detection Latency**
    - **Property 2: Wake Word Detector CPU Usage**
    - **Property 3: Wake Word Detection Accuracy**
    - **Property 4: Wake Word False Positive Rejection**
    - **Property 5: Wake Word Suppression During Processing**
    - **Validates: Requirements 1.2, 1.3, 1.4, 1.5, 1.6**

- [ ] 6. Implement Voice Activity Detector
  - [ ] 6.1 Create vad.py module
    - Integrate Silero VAD PyTorch model
    - Process audio in 30ms chunks (480 samples at 16kHz)
    - Implement speech probability threshold (default 0.5)
    - Add silence timeout detection (1.5 seconds)
    - Implement maximum speech duration limit (30 seconds)
    - Add callbacks for speech start/end events
    - _Requirements: 2.1, 2.2, 2.3, 2.6_

  - [ ]* 6.2 Write property tests for VAD
    - **Property 6: VAD Speech Buffering**
    - **Property 7: VAD Silence Detection**
    - **Property 8: VAD Speech Classification Accuracy**
    - **Property 9: VAD CPU Usage**
    - **Validates: Requirements 2.2, 2.3, 2.4, 2.5**

- [ ] 7. Implement State Machine
  - [ ] 7.1 Create state_machine.py module
    - Define State enum (idle, listening, processing, speaking)
    - Implement StateMachine class with transition logic
    - Enforce valid state transitions
    - Add state change callbacks
    - Coordinate component lifecycle (start/stop)
    - _Requirements: 1.6, 14.6_

  - [ ]* 7.2 Write unit tests for state transitions
    - Test all valid transitions (idle→listening→processing→speaking→idle)
    - Test invalid transitions are rejected
    - Test error transitions (any→idle)
    - _Requirements: 1.6_

- [ ] 8. Checkpoint - Pi Client Foundation Complete
  - Verify all audio components work independently
  - Test wake word detection with sample audio
  - Test VAD with speech samples
  - Ensure all tests pass, ask the user if questions arise


- [ ] 9. Implement WebSocket Message Protocol
  - [ ] 9.1 Create message_protocol.py module
    - Define message schema (version, message_type, device_id, timestamp, payload)
    - Implement message serialization (Python dict → JSON)
    - Implement message parsing (JSON → Python dict)
    - Support client message types: audio_chunk, end_of_stream, heartbeat, error
    - Support server message types: audio_chunk, transcript, answer_text, end_of_response, error
    - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5_

  - [ ]* 9.2 Write property tests for message protocol
    - **Property 58: WebSocket Message Format**
    - **Property 59: Client Message Type Support**
    - **Property 60: Backend Response Format**
    - **Property 61: Backend Message Type Support**
    - **Property 62: Protocol Version Field**
    - **Property 63: Message Serialization Round-Trip**
    - **Validates: Requirements 17.1, 17.2, 17.3, 17.4, 17.5, 17.6**

- [ ] 10. Implement Opus Codec Integration
  - [ ] 10.1 Create opus_codec.py module
    - Implement OpusEncoder class (PCM → Opus)
    - Implement OpusDecoder class (Opus → PCM)
    - Configure for 16kHz sample rate, 24 kbps bitrate, 20ms frame size
    - Add error handling for codec failures
    - _Requirements: 5.6, 16.2, 16.3, 16.5_

  - [ ]* 10.2 Write property test for codec round-trip quality
    - **Property 18: Opus Audio Compression**
    - **Property 54: Backend Opus Decoding**
    - **Property 56: MP3 to Opus Transcoding**
    - **Property 57: Audio Codec Round-Trip Quality**
    - **Validates: Requirements 5.6, 16.2, 16.3, 16.5, 16.6**

- [ ] 11. Implement WebSocket Client
  - [ ] 11.1 Create websocket_client.py module
    - Implement WebSocketClient class using websockets library
    - Add connection establishment with authentication
    - Implement exponential backoff reconnection (1s, 2s, 4s, 8s, max 30s)
    - Add heartbeat mechanism (30 second interval)
    - Implement message queue for disconnection periods
    - Add callbacks for message reception and disconnection
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.6_

  - [ ]* 11.2 Write property tests for WebSocket client
    - **Property 12: WebSocket Authentication Before Data**
    - **Property 13: WebSocket Reconnection Backoff**
    - **Property 14: WebSocket Heartbeat Interval**
    - **Property 15: WebSocket Connection Ready Time**
    - **Validates: Requirements 4.2, 4.3, 4.4, 4.6**

- [ ] 12. Implement Audio Streaming Pipeline
  - [ ] 12.1 Create audio_streamer.py module
    - Integrate AudioCapture, OpusEncoder, and WebSocketClient
    - Stream audio chunks in real-time (no batching)
    - Add metadata to each chunk (device_id, timestamp, sequence number)
    - Implement end-of-stream marker sending
    - Handle network latency and buffering
    - _Requirements: 5.1, 5.2, 5.3, 5.5_

  - [ ]* 12.2 Write property tests for audio streaming
    - **Property 16: Audio Streaming Real-Time**
    - **Property 17: Audio Chunk Transmission Latency**
    - **Validates: Requirements 5.1, 5.2**

- [ ] 13. Integrate Pi Client Components
  - [ ] 13.1 Create pi_client.py main application
    - Wire together all components (wake word, VAD, audio, WebSocket, state machine)
    - Implement main event loop
    - Add graceful shutdown handling
    - Implement error recovery and component restart
    - _Requirements: 1.1, 2.1, 4.1, 14.6_

  - [ ]* 13.2 Write integration tests for Pi Client
    - Test wake word → VAD → streaming pipeline
    - Test state transitions during query flow
    - Test error recovery and reconnection
    - _Requirements: 1.1, 2.1, 4.1_

- [ ] 14. Checkpoint - WebSocket Communication Working
  - Test Pi Client can connect to mock WebSocket server
  - Verify audio streaming with sequence numbers
  - Test reconnection logic with simulated disconnections
  - Ensure all tests pass, ask the user if questions arise


- [ ] 15. Set up Voice Backend project structure
  - Create student/voice_backend/ directory structure
  - Create requirements.txt with dependencies: fastapi, uvicorn, websockets, boto3, python-multipart
  - Create main.py FastAPI application entry point
  - Set up environment variable configuration (.env support)
  - Configure Python logging with CloudWatch integration
  - _Requirements: 7.1, 19.2, 19.3_

- [ ] 16. Implement FastAPI WebSocket Server
  - [ ] 16.1 Create websocket_server.py module
    - Implement FastAPI WebSocket endpoint (/voice)
    - Add connection lifecycle management (accept, handle, close)
    - Implement message routing to processing pipeline
    - Add error handling and logging
    - _Requirements: 7.1, 7.6_

  - [ ]* 16.2 Write unit tests for WebSocket server
    - Test connection acceptance
    - Test message routing
    - Test error handling
    - _Requirements: 7.1_

- [ ] 17. Implement Connection Manager
  - [ ] 17.1 Create connection_manager.py module
    - Implement in-memory connection registry (device_id → WebSocket)
    - Track connection metadata (connect time, message count, last activity)
    - Implement rate limiting (10 queries/minute per device)
    - Add connection cleanup on disconnect
    - _Requirements: 15.1, 15.4, 15.6_

  - [ ]* 17.2 Write property tests for connection manager
    - **Property 50: API Gateway Connection Capacity**
    - **Property 51: Concurrent Query Independence**
    - **Property 53: Device Rate Limiting**
    - **Validates: Requirements 15.1, 15.4, 15.6**

- [ ] 18. Implement Error Handler
  - [ ] 18.1 Create error_handler.py module
    - Define error categories and error codes
    - Implement error logging with context
    - Generate user-friendly error messages
    - Emit CloudWatch metrics for errors
    - Create error message templates
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 19.2, 19.3_

  - [ ]* 18.2 Write unit tests for error handling
    - Test error message generation
    - Test CloudWatch metric emission
    - Test error logging format
    - **Property 48: Error Logging Format**
    - **Validates: Requirements 14.5**

- [ ] 19. Implement AWS Transcribe Streaming Client
  - [ ] 19.1 Create transcribe_client.py module
    - Integrate boto3 transcribe-streaming client
    - Start transcription stream with language code
    - Send audio chunks as they arrive
    - Receive partial and final transcripts
    - Handle transcription errors and timeouts
    - _Requirements: 8.1, 8.2, 8.3, 8.6_

  - [ ]* 19.2 Write property tests for transcription
    - **Property 27: Transcription Partial Results**
    - **Property 28: Transcription Confidence Scores**
    - **Property 29: Transcription Word Accuracy**
    - **Property 30: Multi-Language Transcription Support**
    - **Validates: Requirements 8.2, 8.3, 8.4, 8.6**

- [ ] 20. Implement Knowledge Base Query Client
  - [ ] 20.1 Create knowledge_base_client.py module
    - Integrate boto3 bedrock-agent-runtime client
    - Call retrieve API with query text
    - Return top 5 results with relevance scores
    - Include document metadata (title, page, source)
    - Format retrieved chunks into context string
    - Handle timeouts and no-results cases
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

  - [ ]* 20.2 Write property tests for knowledge base queries
    - **Property 31: Knowledge Base Result Count**
    - **Property 32: Knowledge Base Relevance Scores**
    - **Property 33: Knowledge Base Query Latency**
    - **Property 34: Knowledge Base Document Metadata**
    - **Validates: Requirements 9.2, 9.3, 9.4, 9.6**

- [ ] 21. Implement Answer Generator (Claude)
  - [ ] 21.1 Create answer_generator.py module
    - Integrate boto3 bedrock-runtime client
    - Build system prompt with context and grade level
    - Invoke Claude model with streaming
    - Limit response to 150 words
    - Include source citations in response
    - Handle content policy violations
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_

  - [ ]* 21.2 Write property tests for answer generation
    - **Property 35: Answer Source Citations**
    - **Property 36: Answer Generation Latency**
    - **Property 37: Answer Length Limit**
    - **Validates: Requirements 10.3, 10.4, 10.5**

- [ ] 22. Implement TTS Streaming Client (Polly)
  - [ ] 22.1 Create tts_client.py module
    - Integrate boto3 polly client
    - Synthesize speech with child-friendly voices
    - Stream audio chunks as generated
    - Transcode MP3 to Opus format
    - Support multiple languages (English, Spanish, French, Hindi, Arabic)
    - Configure speech rate (150-160 WPM)
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 16.4, 16.5_

  - [ ]* 22.2 Write property tests for TTS
    - **Property 38: TTS Audio Streaming**
    - **Property 39: TTS Speaking Rate**
    - **Property 40: TTS Multi-Language Support**
    - **Property 41: TTS Speech Marks**
    - **Property 55: TTS MP3 Output Format**
    - **Validates: Requirements 11.3, 11.4, 11.5, 11.6, 16.4**

- [ ] 23. Implement Backend Processing Pipeline
  - [ ] 23.1 Create processing_pipeline.py module
    - Wire together Transcribe, Knowledge Base, Claude, and Polly
    - Implement audio reception and buffering
    - Handle chunk sequencing and reordering
    - Stream TTS audio back to client
    - Add end-to-end latency tracking
    - _Requirements: 7.3, 7.4, 7.5, 12.1, 12.2, 19.4_

  - [ ]* 23.2 Write property tests for processing pipeline
    - **Property 24: Audio Chunk Sequence Ordering**
    - **Property 25: Missing Chunk Detection**
    - **Property 26: Out-of-Order Chunk Reordering**
    - **Property 42: TTS Chunk Streaming Latency**
    - **Property 43: Backend Opus Compression**
    - **Property 69: End-to-End Latency Tracking**
    - **Validates: Requirements 7.3, 7.4, 7.5, 12.2, 12.5, 19.4**

- [ ] 24. Checkpoint - Backend Processing Pipeline Complete
  - Test backend with mock audio input
  - Verify transcription → KB → Claude → TTS flow
  - Test error handling at each stage
  - Measure end-to-end latency
  - Ensure all tests pass, ask the user if questions arise


- [ ] 25. Implement IoT Core Authentication
  - [ ] 25.1 Create iot_authenticator.py module
    - Integrate boto3 IoT Core client
    - Extract certificate from WebSocket connection
    - Call DescribeCertificate API for validation
    - Verify certificate is active and not revoked
    - Implement validation result caching (5 minute TTL)
    - Extract device_id from certificate
    - _Requirements: 6.1, 6.2, 6.3, 7.2_

  - [ ]* 25.2 Write property tests for authentication
    - **Property 19: Device Certificate Uniqueness**
    - **Property 20: Invalid Certificate Rejection**
    - **Property 21: Certificate Read-Only Storage**
    - **Property 22: Certificate Rotation Without Reboot**
    - **Property 23: Backend Authentication Validation**
    - **Validates: Requirements 6.2, 6.3, 6.4, 6.5, 7.2**

- [ ] 26. Integrate Authentication with WebSocket Server
  - [ ] 26.1 Add authentication to WebSocket endpoint
    - Call IoT_Authenticator before accepting connection
    - Reject connections with invalid certificates
    - Pass device_id to Connection Manager
    - Log authentication events
    - _Requirements: 4.2, 6.1, 6.3, 7.2_

  - [ ]* 26.2 Write integration tests for authenticated connections
    - Test valid certificate acceptance
    - Test invalid certificate rejection
    - Test expired certificate rejection
    - _Requirements: 6.3, 7.2_

- [ ] 27. Create Device Provisioning Scripts
  - [ ] 27.1 Create provision_device.py script
    - Generate X.509 certificate via IoT Core
    - Create IoT Thing in registry
    - Attach certificate to Thing
    - Generate config.json with device_id and certificate paths
    - Save certificate and private key to /etc/miro/certs/
    - _Requirements: 6.2, 6.4, 18.2, 18.6_

  - [ ]* 27.2 Write unit tests for provisioning script
    - Test certificate generation
    - Test config.json creation
    - Test file permissions (read-only for certificates)
    - _Requirements: 6.4, 18.2_

- [ ] 28. Checkpoint - Authentication Integrated
  - Test end-to-end authentication flow
  - Verify certificate validation works
  - Test certificate rejection scenarios
  - Ensure all tests pass, ask the user if questions arise


- [ ] 29. Implement CloudWatch Metrics
  - [ ] 29.1 Create metrics_client.py module
    - Integrate boto3 CloudWatch client
    - Emit ConnectionCount gauge metric
    - Emit QueryLatency metric (milliseconds)
    - Emit TranscriptionLatency, KnowledgeBaseLatency, AnswerGenerationLatency, TTSLatency metrics
    - Emit ErrorRate counter metric
    - Emit ErrorType metric with dimensions
    - _Requirements: 19.2, 19.4_

  - [ ]* 29.2 Write property tests for metrics
    - **Property 67: CloudWatch Metrics Emission**
    - **Validates: Requirements 19.2**

- [ ] 30. Implement Logging Infrastructure
  - [ ] 30.1 Configure structured logging for Pi Client
    - Set up Python logging to /var/log/miro/client.log
    - Include device_id in all log messages
    - Add log rotation configuration
    - Implement log levels (DEBUG, INFO, WARNING, ERROR)
    - _Requirements: 19.1, 19.6_

  - [ ] 30.2 Configure structured logging for Voice Backend
    - Set up Python logging with CloudWatch integration
    - Include device_id and request_id in all log messages
    - Log errors with stack traces
    - Implement structured JSON logging format
    - _Requirements: 19.3, 19.5_

  - [ ]* 30.3 Write property tests for logging
    - **Property 48: Error Logging Format**
    - **Property 68: Error Stack Trace Logging**
    - **Property 70: Log Message Device ID**
    - **Validates: Requirements 14.5, 19.3, 19.6**

- [ ] 31. Implement CloudWatch Alarms
  - [ ] 31.1 Create alarm configuration
    - Define alarm for ErrorRate > 5% over 5 minutes
    - Define alarm for QueryLatency p99 > 5000ms
    - Define alarm for ConnectionFailureRate > 10% over 5 minutes
    - Define alarm for HealthCheckFailures > 3 consecutive
    - Configure SNS notifications for all alarms
    - _Requirements: 19.5_

  - [ ]* 31.2 Write unit tests for alarm triggers
    - Test alarm threshold calculations
    - Test SNS notification formatting
    - _Requirements: 19.5_

- [ ] 32. Implement Audio Feedback System
  - [ ] 32.1 Create audio_feedback.py module
    - Generate audio tones for state transitions
    - Create spoken error messages (pre-recorded or TTS)
    - Implement feedback for wake word detected, processing, speaking states
    - Add error feedback messages (connection error, authentication failed, etc.)
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.6_

  - [ ]* 32.2 Write property test for state transition feedback
    - **Property 49: State Transition Audio Feedback**
    - **Validates: Requirements 14.6**

- [ ] 33. Implement Resource Monitoring
  - [ ] 33.1 Create resource_monitor.py module for Pi Client
    - Monitor CPU usage (psutil library)
    - Monitor memory usage
    - Monitor CPU temperature (Raspberry Pi specific)
    - Trigger warnings when thresholds exceeded (CPU >30%, RAM >200MB, temp >80°C)
    - Implement garbage collection trigger for high memory
    - _Requirements: 20.1, 20.2, 20.3, 20.4_

  - [ ]* 33.2 Write property tests for resource constraints
    - **Property 71: Pi Client CPU Usage**
    - **Property 72: Pi Client Memory Usage**
    - **Property 73: Idle Resource Release**
    - **Validates: Requirements 20.1, 20.2, 20.4**

- [ ] 34. Checkpoint - Monitoring and Logging Complete
  - Verify CloudWatch metrics are being emitted
  - Check log files contain proper structure and device_id
  - Test alarm triggers with simulated errors
  - Monitor resource usage during operation
  - Ensure all tests pass, ask the user if questions arise


- [ ] 35. Implement Property-Based Test Suite
  - [ ] 35.1 Set up Hypothesis testing framework
    - Add hypothesis to requirements.txt
    - Create tests/property/ directory structure
    - Configure hypothesis settings (max_examples=100)
    - Create custom generators for audio, messages, configurations
    - _Requirements: All_

  - [ ] 35.2 Create custom test generators
    - Implement audio_with_wake_word_strategy() generator
    - Implement websocket_message_strategy() generator
    - Implement pcm_audio_strategy() generator
    - Implement configuration_strategy() generator
    - Add helper functions for PESQ score calculation
    - _Requirements: All_

  - [ ]* 35.3 Implement remaining property tests
    - Group and implement all 73 properties from design document
    - Ensure each test references property number in docstring
    - Verify all tests run with 100 iterations minimum
    - Add shrinking for minimal failing examples
    - _Requirements: All_

- [ ] 36. Implement Unit Test Suite
  - [ ]* 36.1 Create unit tests for edge cases
    - Test maximum speech duration (30 seconds)
    - Test audio buffer overflow (>5MB)
    - Test WebSocket reconnection after 5 failures
    - Test low transcription confidence (<70%)
    - Test no relevant knowledge base results
    - Test memory usage exceeding 250MB
    - _Requirements: 2.6, 3.6, 4.5, 8.5, 9.5, 20.6_

  - [ ]* 36.2 Create unit tests for error conditions
    - Test invalid device certificate
    - Test malformed WebSocket messages
    - Test network timeout during streaming
    - Test TTS service unavailable
    - Test configuration file missing required fields
    - _Requirements: 6.3, 14.1, 14.2, 14.3, 14.4, 18.4_

- [ ] 37. Implement Integration Test Suite
  - [ ]* 37.1 Create integration tests for component boundaries
    - Test wake word detector → VAD handoff
    - Test VAD → WebSocket streaming
    - Test WebSocket → Backend processing pipeline
    - Test Backend → TTS → Playback
    - _Requirements: 1.1, 2.1, 5.1, 11.1, 13.1_

  - [ ]* 37.2 Create integration tests for error recovery
    - Test WebSocket disconnect mid-stream and reconnection
    - Test low confidence transcription and clarification request
    - Test knowledge base timeout and retry
    - Test component restart after failure
    - _Requirements: 4.3, 8.5, 9.4, 14.1_

- [ ] 38. Implement Load Test Suite
  - [ ]* 38.1 Create load tests for scalability
    - Test 100 concurrent WebSocket connections
    - Test 50 concurrent queries with latency measurement
    - Test rate limiting (10 queries/minute per device)
    - Test Fargate auto-scaling trigger
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6_

  - [ ]* 38.2 Create performance tests for resource constraints
    - Monitor Pi_Client CPU usage over 1 hour
    - Monitor Pi_Client memory usage over 1 hour
    - Run continuous queries for 1 hour and check thermal throttling
    - Run Pi_Client for 7 days and verify stability
    - _Requirements: 20.1, 20.2, 20.3, 20.5_

- [ ] 39. Checkpoint - Testing Complete
  - Run full test suite (unit, property, integration, load)
  - Verify all 73 properties pass
  - Check test coverage >80%
  - Review and fix any failing tests
  - Ensure all tests pass, ask the user if questions arise


- [ ] 40. Create Infrastructure as Code (Terraform)
  - [ ] 40.1 Create terraform/ directory structure
    - Set up Terraform backend configuration (S3 + DynamoDB)
    - Create variables.tf with configurable parameters
    - Create outputs.tf for resource references
    - _Requirements: 15.1, 15.2_

  - [ ] 40.2 Define API Gateway WebSocket API
    - Create API Gateway WebSocket API resource
    - Define routes ($connect, $disconnect, $default)
    - Configure custom authorizer for IoT Core authentication
    - Set up stage and deployment
    - _Requirements: 4.1, 6.1, 7.1, 15.1_

  - [ ] 40.3 Define Fargate Service
    - Create ECS cluster resource
    - Define task definition for Voice_Backend
    - Configure container with environment variables
    - Set up service with auto-scaling (CPU/memory based)
    - Define target group and load balancer integration
    - _Requirements: 7.1, 15.2, 15.3_

  - [ ] 40.4 Define VPC and Networking
    - Create VPC with public and private subnets
    - Configure security groups for Fargate tasks
    - Set up NAT gateway for outbound traffic
    - Define VPC endpoints for AWS services (Bedrock, Polly, Transcribe)
    - _Requirements: 7.1, 15.1_

  - [ ] 40.5 Define IoT Core Resources
    - Create IoT Core thing type for classroom devices
    - Define IoT policy for device permissions
    - Set up certificate registration workflow
    - _Requirements: 6.1, 6.2, 6.3_

  - [ ] 40.6 Define IAM Roles and Policies
    - Create Fargate task execution role
    - Create Fargate task role with permissions (Transcribe, Bedrock, Polly, IoT Core, CloudWatch)
    - Create API Gateway invocation role
    - Define least-privilege policies
    - _Requirements: 6.1, 7.2, 8.1, 9.1, 10.1, 11.1, 19.2_

  - [ ] 40.7 Define CloudWatch Resources
    - Create log groups for Pi_Client and Voice_Backend
    - Define CloudWatch alarms (error rate, latency, connection failures)
    - Set up SNS topic for alarm notifications
    - Create CloudWatch dashboard for monitoring
    - _Requirements: 19.2, 19.3, 19.5_

- [ ] 41. Create Deployment Scripts
  - [ ] 41.1 Create deploy_backend.sh script
    - Build Docker image for Voice_Backend
    - Push image to ECR
    - Run terraform apply for infrastructure
    - Update ECS service with new task definition
    - _Requirements: 15.2_

  - [ ] 41.2 Create deploy_pi_client.sh script
    - Package Pi_Client as systemd service
    - Create installation script for Raspberry Pi
    - Set up log rotation configuration
    - Configure automatic startup on boot
    - _Requirements: 18.1, 19.1, 20.5_

  - [ ] 41.3 Create provision_device.sh wrapper script
    - Call provision_device.py to generate certificate
    - Install certificate to /etc/miro/certs/
    - Generate config.json from template
    - Set file permissions (read-only for certificates)
    - Register device in inventory system
    - _Requirements: 6.2, 6.4, 18.2, 18.6_

- [ ] 42. Create Docker Configuration
  - [ ] 42.1 Create Dockerfile for Voice_Backend
    - Use Python 3.11 slim base image
    - Install dependencies from requirements.txt
    - Copy application code
    - Set up non-root user
    - Configure health check endpoint
    - _Requirements: 7.1, 15.2_

  - [ ] 42.2 Create docker-compose.yml for local development
    - Define Voice_Backend service
    - Add LocalStack for AWS service mocking
    - Configure environment variables
    - Set up volume mounts for development
    - _Requirements: 7.1_

- [ ] 43. Create Documentation
  - [ ] 43.1 Create README.md for Pi_Client
    - Document installation steps
    - List hardware requirements (Raspberry Pi 4, microphone, speaker)
    - Explain configuration options
    - Provide troubleshooting guide
    - _Requirements: 18.1, 18.2, 20.1, 20.2_

  - [ ] 43.2 Create README.md for Voice_Backend
    - Document deployment process
    - List AWS service dependencies
    - Explain environment variables
    - Provide API documentation
    - _Requirements: 7.1, 15.1, 15.2_

  - [ ] 43.3 Create OPERATIONS.md
    - Document monitoring and alerting
    - Explain CloudWatch metrics and alarms
    - Provide runbook for common issues
    - Document scaling procedures
    - _Requirements: 19.2, 19.5, 15.2, 15.3_

- [ ] 44. Final Integration and Testing
  - [ ] 44.1 Deploy complete system to staging environment
    - Deploy infrastructure via Terraform
    - Deploy Voice_Backend to Fargate
    - Provision test Raspberry Pi device
    - Install Pi_Client on test device
    - _Requirements: All_

  - [ ] 44.2 Run end-to-end integration tests
    - Test complete query flow (wake word → answer playback)
    - Verify authentication works
    - Test error recovery scenarios
    - Measure end-to-end latency (<3 seconds)
    - Monitor resource usage on Pi
    - _Requirements: All_

  - [ ]* 44.3 Run load tests in staging
    - Simulate 100 concurrent devices
    - Verify auto-scaling works
    - Check CloudWatch metrics and alarms
    - Validate rate limiting
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6_

  - [ ]* 44.4 Run 7-day stability test
    - Keep Pi_Client running for 7 days
    - Monitor for memory leaks
    - Check for thermal throttling
    - Verify no crashes or restarts needed
    - **Property 52: Response Time Under Load**
    - **Validates: Requirements 20.5**

- [ ] 45. Final Checkpoint - System Complete
  - All components implemented and tested
  - Infrastructure deployed and operational
  - Documentation complete
  - All 73 properties verified
  - System ready for production deployment
  - Ensure all tests pass, ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties from the design document
- Checkpoints ensure incremental validation at major milestones
- All implementation is in Python using libraries specified in design document
- Pi_Client code goes in `student/pi_client/` directory
- Voice_Backend code goes in `student/voice_backend/` directory
- Infrastructure code goes in `student/infrastructure/` directory
- Testing follows dual approach: unit tests for specific cases, property tests for universal properties
- Minimum 100 iterations per property test using Hypothesis library
- All code must be production-ready with proper error handling and logging
