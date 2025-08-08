from modules import Processor
from functools import lru_cache

@lru_cache()
def get_processor() -> Processor:
    return Processor()