
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

HOST = "127.0.0.1"
PORT = 8080

app = FastAPI(
    title="Simple RTMaps control web-based UI",
    version="1.0.0",
    description="A simple web page addressing the RTMaps REST API to control an RTMaps process over the web."
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/",
    StaticFiles(directory="webui", html=True),
    name="rtmaps_webui"
)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        reload=False
    )
