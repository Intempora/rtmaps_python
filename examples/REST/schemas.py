from pydantic import BaseModel, Field
from enum import Enum

class ParseRequest(BaseModel):
    command: str

class LoadDiagramRequest(BaseModel):
    filename: str
    reset: bool = Field(default=False)

class EmptyResponse(BaseModel):
    status: str = Field(default="OK")

class DiagramStateResponse(BaseModel):
    running: bool = Field(default=False)

