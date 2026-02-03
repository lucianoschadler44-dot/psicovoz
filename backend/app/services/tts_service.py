"""
PSICOVOZ - TTS Service (modo texto)
"""
from loguru import logger


class TTSService:
    """Servico mock - modo texto apenas."""
    
    def __init__(self):
        logger.info("🔊 TTS Service inicializado (modo texto)")
    
    async def synthesize(self, text: str, approach: str = None) -> bytes:
        return b""
    
    def get_voice_for_approach(self, approach: str) -> dict:
        return {"speed": 1.0, "pitch": 1.0}
