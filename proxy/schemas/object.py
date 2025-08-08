from pydantic import BaseModel, Field

class ObjectData(BaseModel):
    detected: bool
    x: float = Field(None, ge=-1, le=1)
    y: float = Field(None, ge=-1, le=1)
    a: float = Field(None, ge= 0, le=1)