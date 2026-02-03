"""
PSICOVOZ - Text-to-Speech (texto para voz) Service (servico)
Usa gTTS (Google Text-to-Speech / Google Texto para Voz)
"""
from gtts import gTTS
import tempfile
import io
from loguru import logger


class TTSService:
    """Servico de sintese de voz usando gTTS."""
    
    def __init__(self):
        logger.info("🔊 TTS Service inicializado (gTTS)")
    
    async def synthesize(self, text: str) -> bytes:
        """
        Converte texto em audio MP3.
        
        Args:
            text: Texto para sintetizar
            
        Returns:
            bytes do audio MP3
        """
        if not text.strip():
            return b""
        
        try:
            logger.info(f"🎵 Sintetizando: {text[:30]}...")
            
            # Gerar audio com gTTS
            tts = gTTS(text=text, lang='pt-br', slow=False)
            
            # Salvar em buffer (memoria temporaria)
            buffer = io.BytesIO()
            tts.write_to_fp(buffer)
            buffer.seek(0)
            
            audio_bytes = buffer.read()
            logger.info(f"✅ Audio gerado: {len(audio_bytes)} bytes")
            
            return audio_bytes
            
        except Exception as e:
            logger.error(f"❌ Erro TTS: {e}")
            return b""
    
    def get_voice_for_approach(self, approach: str) -> dict:
        """Retorna config de voz para abordagem."""
        voices = {
            "psicanalise": {"speed": 0.9, "pitch": 0.95},
            "behaviorismo": {"speed": 1.0, "pitch": 1.0},
            "gestalt": {"speed": 0.95, "pitch": 1.05}
        }
        return voices.get(approach, voices["psicanalise"])
