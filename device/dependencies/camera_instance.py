from modules import Gemini
from functools import lru_cache

@lru_cache()
def get_gemini() -> Gemini:
    return Gemini()