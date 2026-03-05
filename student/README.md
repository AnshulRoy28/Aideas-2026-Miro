# Miro Student Component

Baymax-inspired learning companion with voice interaction and RAG-powered answers.

## Architecture

```
student/
├── server.py           # FastAPI backend (port 8001)
├── query.py            # CLI query tool (original)
├── prompt.txt          # System prompt
├── main.js             # Electron main process
├── package.json        # Electron dependencies
└── frontend/
    ├── index.html      # Baymax UI
    ├── styles.css      # Animations & styling
    └── renderer.js     # Frontend logic
```

## Quick Start

### 1. Start Backend Server

```bash
cd student
python server.py
```

Server runs on `http://localhost:8001`

### 2. Install Electron Dependencies

```bash
npm install
```

### 3. Run Electron App

```bash
npm start
```

## Features

- Baymax-style animated character
- Voice input (Web Speech API)
- Text-to-speech responses
- Breathing/idle animations
- Thinking state (pulsing glow)
- Speaking state (lip-sync mouth)
- Jiggle on tap
- RAG-powered answers from knowledge base

## Raspberry Pi Deployment

### Build for ARM

```bash
npm run build:pi
```

### Install on Pi

```bash
# Copy dist/*.AppImage or *.deb to Pi
sudo dpkg -i miro-student_1.0.0_armv7l.deb
```

### Auto-start on Boot

Create `/etc/systemd/system/miro-student.service`:

```ini
[Unit]
Description=Miro Student Backend
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/miro/student
ExecStart=/usr/bin/python3 server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable miro-student
sudo systemctl start miro-student
```

## Design Spec

Based on Baymax design document:
- Weighted pear shape body
- Breathing animation (4s cycle)
- Arm sway
- Eye scanning during thinking
- Audio-reactive mouth
- Tactile minimalism aesthetic

## API Endpoints

### POST /api/query
Query the knowledge base

Request:
```json
{
  "question": "What is photosynthesis?"
}
```

Response:
```json
{
  "answer": "Photosynthesis is...",
  "sources": ["s3://bucket/file.pdf"]
}
```

## Development

Run in dev mode with DevTools:
```bash
npm run dev
```

## Troubleshooting

### "Cannot connect to server"
- Ensure `python server.py` is running
- Check port 8001 is not in use
- Verify `.env` has correct AWS credentials

### Voice input not working
- Check browser permissions for microphone
- Fallback: Click button and type question in prompt

### No audio output
- Check system audio settings
- Verify Web Speech API support in browser
