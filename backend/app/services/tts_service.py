"""
PSICOVOZ - Text-to-Speech Service
Usa Coqui TTS local (GPU)
"""
import torch
import numpy as np
import io
import scipy.io.wavfile as wav
from loguru import logger
from config import settings


class TTSService:
    """Servico de sintese de voz usando Coqui TTS."""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"🔊 TTS Device: {self.device}")
        
        self.model = None
        self.sample_rate = 22050
        self._load_model()
    
    def _load_model(self):
        """Carrega modelo TTS."""
        try:
            from TTS.api import TTS
            
            logger.info(f"📥 Carregando TTS modelo: {settings.TTS_MODEL}")
            self.model = TTS(
                model_name=settings.TTS_MODEL,
                progress_bar=False
            ).to(self.device)
            
            logger.info("✅ Coqui TTS carregado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar TTS: {e}")
            logger.warning("⚠️ Usando TTS fallback (espeak)")
            self.model = None
    
    async def synthesize(self, text: str) -> bytes:
        """
        Converte texto em audio.
        
        Args:
            text: Texto para sintetizar
            
        Returns:
            bytes do audio WAV
        """
        if not text.strip():
            return b""
        
        try:
            if self.model:
                return await self._synthesize_coqui(text)
            else:
                return await self._synthesize_fallback(text)
                
        except Exception as e:
            logger.error(f"❌ Erro TTS: {e}")
            return b""
    
    async def _synthesize_coqui(self, text: str) -> bytes:
        """Sintetiza usando Coqui TTS."""
        logger.info(f"🎵 Sintetizando: {text[:30]}...")
        
        # Gerar audio
        wav_array = self.model.tts(text=text)
        
        # Converter para bytes WAV
        wav_array = np.array(wav_array)
        wav_array = (wav_array * 32767).astype(np.int16)
        
        buffer = io.BytesIO()
        wav.write(buffer, self.sample_rate, wav_array)
        
        audio_bytes = buffer.getvalue()
        logger.info(f"✅ Audio gerado: {len(audio_bytes)} bytes")
        
        return audio_bytes
    
    async def _synthesize_fallback(self, text: str) -> bytes:
        """Fallback usando espeak."""
        import subprocess
        import tempfile
        
        logger.warning("⚠️ Usando espeak fallback")
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name
        
        subprocess.run([
            "espeak-ng", "-v", "pt-br", "-w", temp_path, text
        ], capture_output=True)
        
        with open(temp_path, "rb") as f:
            audio_bytes = f.read()
        
        import os
        os.unlink(temp_path)
        
        return audio_bytes
    
    def get_voice_for_approach(self, approach: str) -> dict:
        """Retorna configuracoes de voz para cada abordagem."""
        voices = {
            "psicanalise": {
                "speed": 0.9,
                "pitch": 0.95,
                "description": "Voz calma e reflexiva"
            },
            "behaviorismo": {
                "speed": 1.0,
                "pitch": 1.0,
                "description": "Voz clara e objetiva"
            },
            "gestalt": {
                "speed": 0.95,
                "pitch": 1.05,
                "description": "Voz calorosa e presente"
            }
        }
        return voices.get(approach, voices["psicanalise"])
