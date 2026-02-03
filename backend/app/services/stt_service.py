"""
PSICOVOZ - STT Service (modo texto)
"""
from loguru import logger


class STTService:
    """Servico mock - modo texto apenas."""
    
    def __init__(self):
        logger.info("🎤 STT Service inicializado (modo texto)")
    
    async def transcribe(self, audio_data: bytes) -> dict:
        return {"text": "", "language": "pt"}
    
    def detect_approach_choice(self, text: str) -> str | None:
        text_lower = text.lower()
        
        keywords = {
            "psicanalise": ["psicanalise", "psicanálise", "freud"],
            "behaviorismo": ["behaviorismo", "comportamental", "skinner", "tcc"],
            "gestalt": ["gestalt", "perls", "aqui agora"]
        }
        
        for approach, words in keywords.items():
            if any(word in text_lower for word in words):
                return approach
        
        if any(w in text_lower for w in ["voce escolhe", "você escolhe", "nao sei", "não sei", "tanto faz"]):
            return "auto"
        
        return None
