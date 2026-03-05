# Memory - System State and Decisions

## Decision - 2026-03-06 Repository Reorganization
**Timestamp**: 2026-03-06

### Decision
Reorganized repository into three component directories: teacher/, student/, infrastructure/

### Reasoning
- Separate teacher-facing (document management) from student-facing (RAG queries)
- Isolate infrastructure code (Lambda functions)
- Improve maintainability and clarity
- Enable independent development of components

### Impact
- Teacher files: server.py, upload scripts, frontend/ → teacher/
- Student files: test.py → student/query.py, prompt.txt → student/
- Infrastructure: lambda/ → infrastructure/lambda/
- Clean separation of concerns

### Next Steps
- Focus on student component development
- Maintain component boundaries

---

## Decision - 2026-03-06 Scope Restriction
**Timestamp**: 2026-03-06

### Decision
Restricted modification scope to `student/` directory only. All other directories require explicit permission.

### Reasoning
- User working on student-facing component
- Need to prevent accidental modifications to teacher or infrastructure code
- Maintain separation of concerns
- Reduce risk of breaking working components

### Impact
- Can only modify files in `student/` directory
- Must request permission for changes outside scope
- Enforces clean component boundaries

### Constraints
ALLOWED:
- Modify any file in `student/`
- Read from other directories for context
- Modify `.env` when explicitly requested

FORBIDDEN without permission:
- `teacher/` directory
- `infrastructure/` directory  
- `docs/` directory
- Root-level files

### Next Steps
- Focus on student-facing component development
- Request permission if cross-component changes needed
- Document all student component changes here


---

## Thought Process - 2026-03-06 Baymax-Style Electron Frontend
**Timestamp**: 2026-03-06

### Goal
Build Baymax-inspired jiggle character frontend for student RAG interface in Electron for Raspberry Pi deployment.

### Constraints
- Must work in `student/` directory only
- Electron app for cross-platform (Raspberry Pi target)
- Integration with existing `query.py` RAG backend
- Design spec: Tactile minimalism, weighted pear shape, breathing animations
- Audio-reactive mouth movements
- State machine: Idle → Thinking → Speaking

### System Components Involved
- `student/query.py` - Existing RAG backend (Python)
- New Electron app (HTML/CSS/JS)
- Web Audio API for lip-sync
- IPC bridge between Electron frontend and Python backend
- SVG/Canvas for character rendering

### Assumptions
- Python backend remains as-is (query.py)
- Electron communicates with Python via subprocess or HTTP
- Raspberry Pi can run Electron + Python
- Audio input/output available on target device

### Risks
- Performance on Raspberry Pi (Electron + Python overhead)
- IPC complexity between Electron and Python
- Audio latency affecting lip-sync quality
- Memory constraints on Pi

### Architecture Decision
**Option 1: Electron + Python Subprocess**
- Electron spawns query.py as subprocess
- Communicate via stdin/stdout JSON
- Pros: Simple, no network needed
- Cons: Process management complexity

**Option 2: Electron + Python HTTP Server**
- query.py runs as FastAPI/Flask server
- Electron makes HTTP requests
- Pros: Clean separation, easier debugging
- Cons: Network overhead, port management

**Recommendation: Option 2 (HTTP Server)**
- Cleaner architecture
- Easier to test components independently
- Can reuse existing FastAPI patterns from teacher component
- Better error handling

### Exact Actions
1. Create Electron app structure in `student/`
2. Convert query.py to FastAPI server (or create new server.py)
3. Build Baymax SVG character with animations
4. Implement Web Audio API for lip-sync
5. Create state machine (Idle/Thinking/Speaking)
6. Wire frontend to backend via HTTP

### Next Steps
- Create student/frontend/ directory structure
- Implement minimal Electron boilerplate
- Create Baymax SVG component
- Add animation engine
- Integrate with query.py backend


---

## Implementation - 2026-03-06 Baymax Electron Frontend
**Timestamp**: 2026-03-06

### Decision
Implemented Baymax-style Electron frontend with FastAPI backend for student component.

### Components Created
1. **student/server.py** - FastAPI backend (port 8001)
   - POST /api/query endpoint
   - Integrates with existing RAG logic
   - Returns answer + sources

2. **student/main.js** - Electron main process
   - Window management
   - 800x900 window size
   - Dev tools in development mode

3. **student/package.json** - Electron configuration
   - Build scripts for Linux/ARM (Raspberry Pi)
   - Electron 28.0.0

4. **student/frontend/index.html** - Baymax UI
   - SVG character with weighted pear shape
   - Face with eyes, bridge, mouth
   - Arm/leg nubs
   - Voice button
   - Response display

5. **student/frontend/styles.css** - Animations
   - Breathing animation (4s cycle)
   - Arm sway
   - Thinking state (pulsing glow)
   - Eye scanning
   - Mouth animation
   - Jiggle on tap
   - Responsive design

6. **student/frontend/renderer.js** - Frontend logic
   - Web Speech API for voice input
   - Text-to-speech for responses
   - State machine (idle/listening/thinking/speaking)
   - HTTP communication with backend
   - Mouth animation during speech

### Architecture
- Backend: Python FastAPI (port 8001)
- Frontend: Electron + HTML/CSS/JS
- Communication: HTTP REST API
- Voice: Web Speech API
- TTS: SpeechSynthesis API

### Features Implemented
✅ Baymax character with breathing animation
✅ Voice input (Web Speech API)
✅ Text-to-speech responses
✅ Thinking state with pulsing glow
✅ Speaking state with mouth animation
✅ Jiggle on tap
✅ RAG integration
✅ Source citations
✅ Raspberry Pi build support

### Next Steps
- Test on Raspberry Pi
- Add Web Audio API for real lip-sync
- Implement noise gate for background noise
- Add confused tilt animation for long latency
- Kid-testing for blink frequency
- Add safety filter visual indicator


---

## Update - 2026-03-06 Requirements and GitIgnore
**Timestamp**: 2026-03-06

### Decision
Updated root-level requirements.txt and .gitignore with user approval.

### Changes Made
1. **requirements.txt**
   - Added comments for clarity
   - Added pydantic>=2.0.0 (required by FastAPI)
   - Organized by component (Python, FastAPI, Auth)

2. **.gitignore**
   - Added Node.js/Electron exclusions
   - node_modules/
   - student/dist/ (Electron build output)
   - package-lock.json
   - npm/yarn logs

### Reasoning
- Student component now uses Electron (Node.js)
- Need to exclude node_modules from git
- FastAPI requires pydantic for data validation
- Better organization of dependencies

### Impact
- Cleaner git repository (no node_modules)
- Complete dependency list for both components
- Easier setup for new developers
