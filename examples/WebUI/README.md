# RTMaps Web Control UI Example

> 🎛 A simple web-based control panel for RTmaps runtime engine using FastAPI + vanilla JS

---

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r ../additionnal_requirements.txt
   ```

2. **Run the server:**
   ```bash
   python rtmaps_web_control_ui.py
   ```

3. **Open in browser:** `http://127.0.0.1:8080/webui/index.html`

---

## Features

- Load `.rtd` diagrams from disk
- Execute diagram commands via REST API  
- Runtime state monitoring (live status updates)
- Integrated log viewer with timestamps
- Clean responsive CSS design

---

## How It Works

```
┌─────────────────────┐     HTTP/REST      ┌──────────────────┐
│   Web UI (port 8080) │ ◄──────────────► │  RTmaps REST API  │
│                     │                    │  (port 8000)      │
│  • Load diagram      │                    │                   │
│  • Parse commands    │◄─────────────────┤│   rtmaps engine   │
│  • Run/Shutdown      │  FastAPI + StaticFiles│• Diagrams         │
│  • State/logs        │                    │• Execution state  │
└─────────────────────┘                    └──────────────────┘
```

---

## Controls

| Button | Action | REST Endpoint |
|--------|--------|---------------|
| 📂 Load | Load `.rtd` diagram file | `/diagram/loaddiagram POST` |
| ▶️ Run | Start diagram execution | `/diagram/run POST` |
| ⏹️ Shutdown | Stop running engine | `/diagram/shutdown POST` |
| Parse | Execute command string | `/diagram/parse POST` |

---

## File Structure

```
WebUI/
├── rtmaps_web_control_ui.py   # FastAPI server
├── additionnal_requirements.txt
└── webui/
    ├── index.html       # UI layout
    ├── app.js           # Frontend logic
    └── style.css        # Styling
```

---

## Requirements

- Python 3.x
- uvicorn, fastapi (from parent requirements)

---
