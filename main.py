import os
import json
import time
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI()

# Mock data stores
with open('data/knowledge_base.json', 'r') as f:
    knowledge_base = json.load(f)

with open('data/customer_history.json', 'r') as f:
    customer_history = json.load(f)

with open('data/fallback_scenarios.json', 'r') as f:
    scenarios = json.load(f)

# Serve static files
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except:
    # Directory doesn't exist yet, will be created
    pass

# Real-time instruction generation
def generate_instructions(scenario_type, audio_text, screen_analysis):
    """Generate step-by-step instructions based on customer issue"""
    
    if scenario_type == "broken_email":
        return {
            "issue_identified": "iPhone Mail app not receiving new emails",
            "confidence": "94%",
            "instructions": [
                "First, let's check if you're connected to WiFi or cellular data. Can you see the WiFi symbol or signal bars at the top of your screen?",
                "Now let's go to Settings. Can you find the Settings app on your home screen? It looks like a gray gear.",
                "Great! Now scroll down and tap on 'Mail'. It should be in the list with a blue envelope icon.",
                "Perfect. Now tap on 'Accounts' at the top of the Mail settings.",
                "I can see your Gmail account here. Tap on your Gmail account to open its settings.",
                "Now tap on 'Account' at the very top - this will show us your email server settings.",
                "Let's check if 'Mail' is turned on. Make sure the toggle next to 'Mail' is green and switched on.",
                "Now let's go back and check 'Fetch New Data'. Tap the back arrow and then tap 'Fetch New Data'.",
                "Change this from 'Manual' to 'Push' - this will make your emails arrive immediately.",
                "Finally, let's restart the Mail app. Double-tap the home button and swipe up on the Mail app to close it, then reopen it."
            ],
            "reference_doc": "Apple Mail Configuration Guide - Gmail IMAP Settings",
            "escalate_if": "Customer still not receiving emails after restart"
        }
    
    elif scenario_type == "scam_popup":
        return {
            "issue_identified": "Fraudulent popup claiming Apple ID compromise",
            "confidence": "98%",
            "instructions": [
                "I can see that popup on your screen. This is definitely a scam - Apple will never show popups like this in Safari.",
                "First, DO NOT tap 'OK' or enter any passwords. Let's close this popup safely.",
                "Hold down the power button and volume up button at the same time until you see 'slide to power off'.",
                "Slide to power off your iPhone completely. This will close Safari and the fake popup.",
                "Wait 10 seconds, then press and hold the power button to turn your iPhone back on.",
                "When it's back on, don't open Safari yet. Let's clear Safari's data first.",
                "Go to Settings, then scroll down to 'Safari'.",
                "Tap 'Clear History and Website Data' - this removes any malicious code.",
                "Tap 'Clear History and Data' to confirm. This is safe and won't affect your other apps.",
                "Now you can safely use Safari again. The scam popup is completely gone.",
                "In the future, if you see popups like this, always close Safari immediately and never enter your password."
            ],
            "reference_doc": "Mister Mac Scam Identification Guide",
            "escalate_if": "Customer already entered personal information in the popup"
        }
    
    else:  # internal_tools
        return {
            "issue_identified": "Customer needs help with iCloud storage management",
            "confidence": "91%", 
            "instructions": [
                "I can see your iCloud storage is almost full. Let's free up some space together.",
                "First, let's check what's using the most storage. Go to Settings on your iPhone.",
                "Tap on your name at the very top - where it shows your Apple ID.",
                "Now tap on 'iCloud' - you should see it in the list below your name.",
                "Tap on 'Manage Storage' - this shows us exactly what's taking up space.",
                "I can see Photos is using most of your storage. Let's optimize that first.",
                "Go back to the main iCloud page and tap on 'Photos'.",
                "Turn on 'Optimize iPhone Storage' - this keeps smaller versions on your phone.",
                "The full-resolution photos stay safely in iCloud, but your phone uses less space.",
                "Now let's clean up old backups. Go back to iCloud settings and tap 'iCloud Backup'.",
                "Tap 'Manage Storage' and look for old device backups you don't need anymore."
            ],
            "reference_doc": "iCloud Storage Management - Mister Mac Internal Guide", 
            "escalate_if": "Customer wants to upgrade iCloud storage plan"
        }

# API Routes
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>Mister Mac AI Tech Support Copilot</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&family=Open+Sans:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&family=Open+Sans:ital,wght@0,400;0,600;1,400&display=swap');

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Open Sans', sans-serif;
            background: #faf9f5;
            color: #4a4845;
            min-height: 100vh;
        }

        h1, h2, h3, h4, h5, button, label, .label, nav, .badge, th {
            font-family: 'Roboto', sans-serif;
        }

        .container {
            max-width: 1100px;
            margin: 0 auto;
            padding: 40px 24px;
        }

        .app-header {
            background: #ffffff;
            border-bottom: 1px solid #e8e6dc;
            padding: 0 24px;
            height: 56px;
            display: flex;
            align-items: center;
            font-family: 'Roboto', sans-serif;
            font-weight: 700;
            color: #141413;
            justify-content: space-between;
        }

        .card {
            background: #ffffff;
            border: 1px solid #e8e6dc;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
        }

        .section-label {
            font-family: 'Roboto', sans-serif;
            font-size: 11px;
            font-weight: 600;
            color: #b0aea5;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 14px;
        }

        .btn-primary {
            background: #d97757;
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 10px 22px;
            font-family: 'Roboto', sans-serif;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            transition: background 0.15s;
        }
        .btn-primary:hover { background: #b85e3a; }
        .btn-primary:disabled { opacity: 0.45; cursor: not-allowed; }

        .btn-secondary {
            background: #f0efe9;
            color: #141413;
            border: 1px solid #e8e6dc;
            border-radius: 8px;
            padding: 10px 22px;
            font-family: 'Roboto', sans-serif;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            margin-right: 12px;
        }
        .btn-secondary:hover { background: #e8e6dc; }

        .badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 20px;
            font-family: 'Roboto', sans-serif;
            font-weight: 600;
            font-size: 12px;
        }
        .badge-green  { color: #788c5d; background: #e8eddf; }
        .badge-orange { color: #d97757; background: #f5e6df; }
        .badge-blue   { color: #6a9bcc; background: #e3eef7; }
        .badge-gray   { color: #b0aea5; background: #f0efe9; }

        .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
        
        .call-status {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #788c5d;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .instructions-panel {
            background: #f0efe9;
            border: 1px solid #e8e6dc;
            border-radius: 12px;
            padding: 24px;
            margin-top: 16px;
        }

        .instruction-step {
            background: #ffffff;
            border: 1px solid #e8e6dc;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
            position: relative;
        }

        .step-number {
            display: inline-block;
            background: #d97757;
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            text-align: center;
            line-height: 24px;
            font-size: 12px;
            font-weight: 600;
            margin-right: 12px;
        }

        .audio-controls {
            margin: 16px 0;
        }

        audio {
            width: 100%;
            max-width: 400px;
        }

        .screen-mockup {
            background: #000;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            color: white;
            font-family: 'Roboto', sans-serif;
            margin: 16px 0;
        }

        .loading-state {
            text-align: center;
            color: #d97757;
            padding: 48px;
            font-family: 'Open Sans', sans-serif;
            font-size: 15px;
        }

        .alert {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 14px;
            border-radius: 8px;
            font-family: 'Open Sans', sans-serif;
            font-size: 14px;
            margin-bottom: 16px;
        }
        .alert-info { background: #e3eef7; border: 1px solid #b8d4eb; color: #4a6a8a; }

        .customer-info {
            background: #ffffff;
            border: 1px solid #e8e6dc;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
        }
    </style>
</head>
<body>
    <header class="app-header">
        <div>🍎 Mister Mac AI Tech Support Copilot</div>
        <div class="call-status">
            <span class="status-dot"></span>
            Ready for Customer Calls
        </div>
    </header>

    <main class="container">
        <div class="alert alert-info">
            🎯 <strong>Demo Mode:</strong> This simulates real-time AI analysis of customer calls and screen shares. In production, connects directly to FaceTime SharePlay.
        </div>

        <div class="two-col">
            <!-- Left Column: Customer Call Interface -->
            <div>
                <div class="section-label">Active Customer Session</div>
                
                <div class="customer-info">
                    <div style="font-weight: 600; margin-bottom: 8px;" id="customerName">No active call</div>
                    <div style="font-size: 13px; color: #b0aea5;" id="customerDetails">Select a scenario to begin</div>
                </div>

                <div class="card">
                    <div class="section-label">Customer Scenarios</div>
                    <div style="margin-bottom: 16px;">
                        <button class="btn-secondary" onclick="startScenario('broken_email')">📧 Broken iPhone Email</button>
                        <button class="btn-secondary" onclick="startScenario('scam_popup')">⚠️ Scam Popup Alert</button>
                        <button class="btn-secondary" onclick="startScenario('internal_tools')">☁️ iCloud Storage Full</button>
                    </div>
                    
                    <div id="audioSection" style="display: none;">
                        <div class="section-label">Customer Audio</div>
                        <div class="audio-controls">
                            <audio id="customerAudio" controls style="width: 100%; margin-bottom: 12px;">
                                Your browser does not support the audio element.
                            </audio>
                        </div>
                    </div>

                    <div id="screenShareSection" style="display: none;">
                        <div class="section-label">Customer Screen Share</div>
                        <div class="screen-mockup" id="screenMockup">
                            🖥️ Connected to customer's iPhone screen
                        </div>
                    </div>

                    <div id="transcriptionSection" style="display: none;">
                        <div class="section-label">Live Transcription</div>
                        <div id="liveTranscript" style="background: #f0efe9; padding: 16px; border-radius: 8px; font-family: 'Open Sans', sans-serif; font-style: italic;">
                        </div>
                    </div>
                </div>
            </div>

            <!-- Right Column: AI Assistant Interface -->
            <div>
                <div class="section-label">AI Analysis & Guidance</div>
                
                <div class="card">
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
                        <div>🧠</div>
                        <div>
                            <div style="font-weight: 600;">AI Status</div>
                            <div style="font-size: 13px; color: #b0aea5;" id="aiStatus">Waiting for customer interaction...</div>
                        </div>
                    </div>

                    <div id="issueAnalysis" style="display: none;">
                        <div class="section-label">Issue Identified</div>
                        <div style="margin-bottom: 16px;">
                            <div id="issueDescription" style="font-weight: 600; margin-bottom: 4px;"></div>
                            <div style="font-size: 13px;">
                                <span class="badge badge-green" id="confidenceLevel"></span>
                                <span style="margin-left: 8px; color: #b0aea5;" id="referenceDoc"></span>
                            </div>
                        </div>
                    </div>

                    <div id="instructionsContainer" style="display: none;">
                        <div class="instructions-panel">
                            <div class="section-label">Step-by-Step Instructions</div>
                            <div style="font-size: 13px; color: #b0aea5; margin-bottom: 16px;">
                                💡 Read these instructions exactly to the customer
                            </div>
                            <div id="instructionsList"></div>
                            
                            <div id="escalationWarning" style="display: none; margin-top: 16px; padding: 12px; background: #fdf3dd; border: 1px solid #f0dba0; border-radius: 8px; color: #7a5a1a; font-size: 13px;">
                                ⚠️ <strong>Escalate to Scott if:</strong> <span id="escalateCondition"></span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Knowledge Base Reference -->
                <div class="card">
                    <div class="section-label">Knowledge Base Quick Access</div>
                    <div style="font-size: 13px; color: #b0aea5; margin-bottom: 12px;">AI references Mister Mac's troubleshooting guides</div>
                    <div id="knowledgeRefs">
                        <div style="padding: 8px; background: #f0efe9; border-radius: 6px; margin-bottom: 8px; font-size: 13px;">📖 Apple Mail Configuration Guide</div>
                        <div style="padding: 8px; background: #f0efe9; border-radius: 6px; margin-bottom: 8px; font-size: 13px;">🛡️ Scam Identification Procedures</div>
                        <div style="padding: 8px; background: #f0efe9; border-radius: 6px; font-size: 13px;">☁️ iCloud Storage Management</div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <script>
        let currentScenario = null;
        
        const scenarios = {
            broken_email: {
                name: "Sarah Johnson",
                details: "iPhone 12, iOS 17.2 • Issue: Gmail not receiving new emails",
                audio: "/static/broken_email.mp3",
                transcript: "Hi, I'm having trouble with my email on my iPhone. I'm not getting any new emails since yesterday. I can send emails but nothing new is coming in. My Gmail works fine on my computer but not on my phone.",
                screen: "📱 iPhone Settings > Mail > Accounts screen visible"
            },
            scam_popup: {
                name: "Robert Chen", 
                details: "iPhone 13, iOS 17.1 • Issue: Suspicious popup appeared in Safari",
                audio: "/static/scam_popup.mp3",
                transcript: "I was browsing the internet and this popup appeared saying my Apple ID has been compromised and I need to verify it immediately. It's asking for my password. Should I click on it? It looks official but I'm not sure.",
                screen: "🚨 Safari showing fake Apple ID security alert popup"
            },
            internal_tools: {
                name: "Maria Rodriguez",
                details: "iPhone 14, iOS 17.3 • Issue: iCloud storage full, can't backup photos", 
                audio: "/static/internal_tools.mp3",
                transcript: "My phone keeps telling me my iCloud storage is full and I can't back up my photos anymore. I don't want to lose my pictures but I don't know how to manage the storage. Can you help me figure out what's taking up all the space?",
                screen: "⚙️ Settings > Apple ID > iCloud > Storage full warning"
            }
        };

        function startScenario(scenarioType) {
            currentScenario = scenarioType;
            const scenario = scenarios[scenarioType];
            
            // Update customer info
            document.getElementById('customerName').textContent = scenario.name;
            document.getElementById('customerDetails').textContent = scenario.details;
            
            // Show audio section
            document.getElementById('audioSection').style.display = 'block';
            const audio = document.getElementById('customerAudio');
            
            // Show screen share
            document.getElementById('screenShareSection').style.display = 'block';
            document.getElementById('screenMockup').innerHTML = scenario.screen;
            
            // Show transcription
            document.getElementById('transcriptionSection').style.display = 'block';
            document.getElementById('liveTranscript').textContent = scenario.transcript;
            
            // Update AI status
            document.getElementById('aiStatus').textContent = 'Analyzing customer audio and screen...';
            
            // Simulate AI processing
            setTimeout(() => {
                analyzeWithAI(scenarioType);
            }, 2000);
        }

        function analyzeWithAI(scenarioType) {
            // Update AI status
            document.getElementById('aiStatus').textContent = 'Generating step-by-step instructions...';
            
            // Fetch AI analysis
            fetch(`/analyze/${scenarioType}`)
                .then(response => response.json())
                .then(data => {
                    // Show issue analysis
                    document.getElementById('issueAnalysis').style.display = 'block';
                    document.getElementById('issueDescription').textContent = data.issue_identified;
                    document.getElementById('confidenceLevel').textContent = `${data.confidence} confidence`;
                    document.getElementById('referenceDoc').textContent = data.reference_doc;
                    
                    // Show instructions
                    document.getElementById('instructionsContainer').style.display = 'block';
                    const instructionsList = document.getElementById('instructionsList');
                    instructionsList.innerHTML = '';
                    
                    data.instructions.forEach((instruction, index) => {
                        const stepDiv = document.createElement('div');
                        stepDiv.className = 'instruction-step';
                        stepDiv.innerHTML = `
                            <span class="step-number">${index + 1}</span>
                            ${instruction}
                        `;
                        instructionsList.appendChild(stepDiv);
                    });
                    
                    // Show escalation warning if needed
                    if (data.escalate_if) {
                        document.getElementById('escalationWarning').style.display = 'block';
                        document.getElementById('escalateCondition').textContent = data.escalate_if;
                    }
                    
                    // Update AI status
                    document.getElementById('aiStatus').textContent = 'Instructions ready - guide customer through steps';
                });
        }
    </script>
</body>
</html>
    """)

@app.get("/analyze/{scenario_type}")
async def analyze_scenario(scenario_type: str):
    """Simulate AI analysis of customer scenario"""
    # Simulate processing delay
    import asyncio
    await asyncio.sleep(1)
    
    # Return AI-generated instructions
    return generate_instructions(scenario_type, "", "")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)