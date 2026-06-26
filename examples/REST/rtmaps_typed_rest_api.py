from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from rtmaps import RTMapsWrapper, RTMapsException
from schema import Schema, And, Use, Optional, SchemaError
import uvicorn

from schemas import (
    ParseRequest,
    LoadDiagramRequest,
    EmptyResponse,
    DiagramStateResponse
)

HOST = "localhost"
PORT = 8000

app = FastAPI(
    title="RTMaps Typed REST API",
    version="1.0.0",
    description="Typed REST API for RTMaps control"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rtmaps = RTMapsWrapper()

@app.post("/diagram/loaddiagram", response_model=EmptyResponse)
def load_diagram(payload: LoadDiagramRequest):
    try:
        rtmaps.load_diagram(
            diagram_path=payload.filename,
            reset=payload.reset
        )
        return EmptyResponse()
    except RTMapsException as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/diagram/parse", response_model=EmptyResponse)
def parse(payload: ParseRequest):
    try:
        rtmaps.parse(
            command = payload.command
        )
        return EmptyResponse()
    except RTMapsException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/diagram/run", response_model=EmptyResponse)
def run():
    try:
        rtmaps.run()
        return EmptyResponse()
    except RTMapsException as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/diagram/shutdown", response_model=EmptyResponse)
def shutdown():
    try:
        rtmaps.shutdown()
        return EmptyResponse()
    except RTMapsException as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/diagram/is_running", response_model=DiagramStateResponse)
def is_running():
    try:
        is_running = rtmaps.is_running()
        return DiagramStateResponse(running = bool(is_running))
    except RTMapsException as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "rtmaps_typed_rest_api:app",
        host=HOST,
        port=PORT,
        reload=False
    )

 