// Baymax Frontend - Renderer Process
// Handles UI interactions and animations

const API_BASE_URL = 'http://localhost:8001';

// DOM Elements
const baymax = document.getElementById('baymax');
const baymaxContainer = document.getElementById('baymax-container');
const body = document.getElementById('body');
const leftEye = document.getElementById('left-eye');
const rightEye = document.getElementById('right-eye');
const status = document.getElementById('status');
const textInput = document.getElementById('text-input');
const sendBtn = document.getElementById('send-btn');
const voiceBtn = document.getElementById('voice-btn');
const responseContainer = document.getElementById('response-container');
const responseText = document.getElementById('response-text');
const sources = document.getElementById('sources');

// State
let currentState = 'idle'; // idle, listening, thinking, speaking
let recognition = null;
let audioContext = null;
let analyser = null;
let animationFrame = null;

// Initialize Speech Recognition
function initSpeechRecognition() {
    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        recognition.onstart = () => {
            setState('listening');
        };
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            console.log('Heard:', transcript);
            handleQuery(transcript);
        };
        
        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            setState('idle');
        };
        
        recognition.onend = () => {
            if (currentState === 'listening') {
                setState('idle');
            }
        };
    } else {
        console.warn('Speech recognition not supported');
    }
}

// Initialize Audio Context for Lip Sync
function initAudioContext() {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    analyser = audioContext.createAnalyser();
    analyser.fftSize = 256;
    analyser.smoothingTimeConstant = 0.2;
}

// Set State
function setState(newState) {
    currentState = newState;
    
    // Update status display
    status.className = `status-${newState}`;
    
    switch(newState) {
        case 'idle':
            status.textContent = 'Ready';
            baymax.classList.remove('thinking', 'speaking');
            voiceBtn.classList.remove('listening');
            sendBtn.disabled = false;
            textInput.disabled = false;
            stopMouthAnimation();
            break;
            
        case 'listening':
            status.textContent = 'Listening...';
            voiceBtn.classList.add('listening');
            sendBtn.disabled = true;
            textInput.disabled = true;
            break;
            
        case 'thinking':
            status.textContent = 'Thinking...';
            baymax.classList.add('thinking');
            baymax.classList.remove('speaking');
            voiceBtn.classList.remove('listening');
            sendBtn.disabled = true;
            textInput.disabled = true;
            break;
            
        case 'speaking':
            status.textContent = 'Speaking';
            baymax.classList.remove('thinking');
            baymax.classList.add('speaking');
            break;
    }
}

// Handle Query
async function handleQuery(question) {
    setState('thinking');
    responseContainer.classList.add('hidden');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question })
        });
        
        if (!response.ok) {
            throw new Error('Query failed');
        }
        
        const data = await response.json();
        
        // Display response
        responseText.textContent = data.answer;
        
        // Display sources
        if (data.sources && data.sources.length > 0) {
            sources.innerHTML = '<strong>Sources:</strong><br>' + 
                data.sources.map((s, i) => `[${i + 1}] ${s}`).join('<br>');
        }
        
        responseContainer.classList.remove('hidden');
        
        // Speak the answer
        speakText(data.answer);
        
    } catch (error) {
        console.error('Query error:', error);
        responseText.textContent = 'Sorry, I encountered an error. Please try again.';
        responseContainer.classList.remove('hidden');
        setState('idle');
    }
}

// Text-to-Speech with AWS Polly
async function speakText(text) {
    // Keep thinking state while generating audio
    // setState('speaking') will be called when audio starts playing
    
    try {
        // Request audio from backend (still in thinking state)
        const response = await fetch(`${API_BASE_URL}/api/tts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                text: text,
                voice_id: 'Ruth'  // Generative voice - more natural
            })
        });
        
        if (!response.ok) {
            throw new Error('TTS failed');
        }
        
        // Get audio blob
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        
        // Create audio element
        const audio = new Audio(audioUrl);
        
        // Switch to speaking state when audio starts
        audio.onplay = () => {
            setState('speaking');
        };
        
        audio.onended = () => {
            URL.revokeObjectURL(audioUrl);
            setState('idle');
        };
        
        audio.onerror = () => {
            URL.revokeObjectURL(audioUrl);
            setState('idle');
        };
        
        // Start playing (will trigger onplay -> speaking state)
        await audio.play();
        
    } catch (error) {
        console.error('TTS error:', error);
        // Fallback to browser TTS if Polly fails
        if ('speechSynthesis' in window) {
            setState('speaking');
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 0.9;
            speechSynthesis.speak(utterance);
            utterance.onend = () => setState('idle');
        } else {
            setState('idle');
        }
    }
}

// Jiggle Animation on Tap
baymaxContainer.addEventListener('click', () => {
    baymax.classList.add('jiggle');
    setTimeout(() => {
        baymax.classList.remove('jiggle');
    }, 500);
});

// Send Button Click
sendBtn.addEventListener('click', () => {
    const question = textInput.value.trim();
    if (question && currentState === 'idle') {
        handleQuery(question);
        textInput.value = '';
    }
});

// Enter Key in Text Input
textInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const question = textInput.value.trim();
        if (question && currentState === 'idle') {
            handleQuery(question);
            textInput.value = '';
        }
    }
});

// Voice Button Click
voiceBtn.addEventListener('click', () => {
    if (currentState === 'idle') {
        if (recognition) {
            recognition.start();
        } else {
            alert('Voice input not supported in this browser. Please type your question.');
        }
    } else if (currentState === 'listening') {
        recognition.stop();
    }
});

// Initialize
initSpeechRecognition();
initAudioContext();
setState('idle');

console.log('Baymax initialized and ready!');
