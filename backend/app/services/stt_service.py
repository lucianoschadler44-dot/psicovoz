"""
PSICOVOZ - Speech-to-Text Service
Usa OpenAI Whisper local
"""
import whisper
import tempfile
import os
import numpy as np
from loguru import logger
from config import settings


class STTService:
    """Servico de reconhecimento de voz usando Whisper."""
    
    def __init__(self):
        logger.info(f"📥 Carregando Whisper modelo: {settings.WHISPER_MODEL}")
        try:
            self.model = whisper.load_model(settings.WHISPER_MODEL)
            logger.info("✅ Whisper carregado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao carregar Whisper: {e}")
            self.model = None
    
    async def transcribe(self, audio_data: bytes) -> dict:
        """
        Transcreve audio para texto.
        
        Args:
            audio_data: Bytes do audio (WAV/WebM)
            
        Returns:
            dict com 'text', 'language'
        """
        if not self.model:
            logger.warning("⚠️ Whisper nao carregado, retornando vazio")
            return {"text": "", "language": "pt"}
        
        try:
            # Salvar audio temporariamente
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(audio_data)
                temp_path = f.name
            
            # Transcrever
            result = self.model.transcribe(
                temp_path,
                language="pt",
                task="transcribe"
            )
            
            # Limpar arquivo temporario
            os.unlink(temp_path)
            
            text = result.get("text", "").strip()
            logger.info(f"📝 Transcricao: {text[:50]}...")
            
            return {
                "text": text,
                "language": result.get("language", "pt")
            }
            
        except Exception as e:
            logger.error(f"❌ Erro STT: {e}")
            return {"text": "", "language": "pt", "error": str(e)}
    
    def detect_approach_choice(self, text: str) -> str | None:
        """Detecta se usuario escolheu uma abordagem."""
        text_lower = text.lower()
        
        keywords = {
            "psicanalise": ["psicanalise", "psicanálise", "freud", "inconsciente"],
            "behaviorismo": ["behaviorismo", "comportamental", "skinner", "tcc", "cognitivo"],
            "gestalt": ["gestalt", "perls", "aqui agora", "aqui e agora"]
        }
        
        for approach, words in keywords.items():
            if any(word in text_lower for word in words):
                return approach
        
        auto_keywords = ["voce escolhe", "você escolhe", "nao sei", "não sei", "tanto faz"]
        if any(word in text_lower for word in auto_keywords):
            return "auto"
        
        return None
