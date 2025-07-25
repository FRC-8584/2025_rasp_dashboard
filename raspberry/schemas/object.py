from pydantic import BaseModel, Field

class ObjectData(BaseModel):
    detected: bool
    x: int = Field(None, ge=0, le=1)
    y: int = Field(None, ge=0, le=1)
    a: int = Field(None, ge=0, le=1)
