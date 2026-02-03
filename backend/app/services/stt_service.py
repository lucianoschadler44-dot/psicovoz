"""
PSICOVOZ - Speech-to-Text Service
Usa OpenAI Whisper local (GPU)
"""
import whisper
import torch
import numpy as np
import tempfile
import os
from loguru import logger
from config import settings


class STTService:
    """Servico de reconhecimento de voz usando Whisper."""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"🎤 STT Device: {self.device}")
        
        logger.info(f"📥 Carregando Whisper modelo: {settings.WHISPER_MODEL}")
        self.model = whisper.load_model(
            settings.WHISPER_MODEL,
            device=self.device
        )
        logger.info("✅ Whisper carregado")
    
    async def transcribe(self, audio_data: bytes) -> dict:
        """
        Transcreve audio para texto.
        
        Args:
            audio_data: Bytes do audio (WAV/MP3)
            
        Returns:
            dict com 'text', 'language', 'confidence'
        """
        try:
            # Salvar audio temporariamente
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(audio_data)
                temp_path = f.name
            
            # Transcrever
            result = self.model.transcribe(
                temp_path,
                language="pt",
                task="transcribe",
                fp16=(self.device == "cuda")
            )
            
            # Limpar arquivo temporario
            os.unlink(temp_path)
            
            text = result.get("text", "").strip()
            logger.info(f"📝 Transcricao: {text[:50]}...")
            
            return {
                "text": text,
                "language": result.get("language", "pt"),
                "segments": result.get("segments", [])
            }
            
        except Exception as e:
            logger.error(f"❌ Erro STT: {e}")
            return {"text": "", "language": "pt", "error": str(e)}
    
    def detect_approach_choice(self, text: str) -> str | None:
        """
        Detecta se usuario escolheu uma abordagem.
        
        Returns:
            'psicanalise', 'behaviorismo', 'gestalt', 'auto' ou None
        """
        text_lower = text.lower()
        
        # Palavras-chave para cada abordagem
        keywords = {
            "psicanalise": ["psicanalise", "psicanálise", "freud", "inconsciente"],
            "behaviorismo": ["behaviorismo", "comportamental", "skinner", "tcc", "cognitivo"],
            "gestalt": ["gestalt", "perls", "aqui agora", "aqui e agora"]
        }
        
        for approach, words in keywords.items():
            if any(word in text_lower for word in words):
                logger.info(f"🎯 Abordagem detectada: {approach}")
                return approach
        
        # Usuario quer que sistema escolha
        auto_keywords = ["voce escolhe", "você escolhe", "nao sei", "não sei", 
                        "tanto faz", "qualquer", "escolha voce", "escolha você"]
        if any(word in text_lower for word in auto_keywords):
            logger.info("🎯 Usuario pediu escolha automatica")
            return "auto"
        
        return None
