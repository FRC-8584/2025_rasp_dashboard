from pydantic import BaseModel, Field
from typing import Literal

class HSV_SCOPE(BaseModel):
    hue_min: int = Field(0  , ge=0, le=180)
    hue_max: int = Field(180, ge=0, le=180)
    sat_min: int = Field(0  , ge=0, le=255)
    sat_max: int = Field(255, ge=0, le=255)
    val_min: int = Field(0  , ge=0, le=255)
    val_max: int = Field(255, ge=0, le=255)

class SettingsModel(BaseModel):
    type:         Literal["color", "coral"] = "color"
    show_as:      Literal["normal", "mask"] = "normal"
    min_area:     int   = Field(10, ge=0, le=100)
    gain:         int   = Field(0, ge=0, le=100)
    black_level:  int   = Field(100, ge=0, le=255)
    red_balance:  int   = Field(1350, ge=0, le=4095)
    blue_balance: int   = Field(1350, ge=0, le=4095)
    hsv_scope:    HSV_SCOPE
    box_object:   bool  = True
