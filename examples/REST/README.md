# RTMaps Typed REST API Example

> 🔌 A typed REST API interface for controlling the RTmaps runtime engine via HTTP endpoints.

---

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r ../additionnal_requirements.txt
   ```

2. **Run the server:**
   ```bash
   python rtmaps_typed_rest_api.py
   ```

3. **Server runs on:** `http://localhost:8000`

---

## Features

- Type-safe REST endpoints using FastAPI
- CORS-enabled for cross-origin requests
- Clean error handling with HTTP exceptions  
- Ready for integration with frontend clients (Web UI, custom apps)
- Schema-based request validation

---

## API Endpoints

| Method | Endpoint | Action | Request Model |
|--------|----------|--------|---------------|
| POST | `/diagram/loaddiagram` | Load `.rtd` diagram file | `LoadDiagramRequest` (filename, reset) |
| POST | `/diagram/parse` | Parse command string | `ParseRequest` (command) |
| POST | `/diagram/run` | Start diagram execution | — (no body required) |
| POST | `/diagram/shutdown` | Stop running engine | — (no body required) |
| GET  | `/diagram/is_running` | Check runtime state | → `DiagramStateResponse` (running bool) |

---

## Architecture

```
┌──────────────────────┐     HTTP/REST      ┌───────────────────┐
│   External Clients   │ ◄────────────────► │  Typed REST API   │
│ • Web UI             │                    │   (port 8000)     │
│ • Custom apps        │ FastAPI + Pydantic │                   │
│ • curl / Postman     │                     │  RTMapsAbstraction │
└──────────────────────┘                    └───────────────────┘
```

---

## File Structure

```
REST/
├── rtmaps_typed_rest_api.py   # FastAPI server & endpoints
├── schemas.py                  # Pydantic request/response models
├── additionnal_requirements.txt
└── __pycache__/
```

---

## Requirements

- Python 3.x
- uvicorn, fastapi, pydantic (from parent requirements)
- rtmaps (RTMapsAbstraction library)

---

## CORS Configuration

By default, all origins (`*`) are allowed. For production use, update `origins` in `rtmaps_typed_rest_api.py`:

```python
origins = [
    "http://localhost:8080",  # Web UI frontend
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---
