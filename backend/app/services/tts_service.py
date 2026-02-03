"""
PSICOVOZ - Text-to-Speech (texto para voz) Service (servico)
Usa Edge TTS (Microsoft) com vozes masculinas PT-BR
"""
import edge_tts
import asyncio
import io
from loguru import logger


class TTSService:
    """Servico de sintese de voz usando Edge TTS."""
    
    # Vozes masculinas PT-BR para cada abordagem
    VOICES = {
        "psicanalise": {
            "voice": "pt-BR-AntonioNeural",
            "rate": "-5%",
            "pitch": "-5Hz"
        },
        "behaviorismo": {
            "voice": "pt-BR-AntonioNeural",
            "rate": "+0%",
            "pitch": "+0Hz"
        },
        "gestalt": {
            "voice": "pt-BR-AntonioNeural",
            "rate": "-3%",
            "pitch": "+3Hz"
        },
        "shadow": {
            "voice": "pt-BR-AntonioNeural",
            "rate": "+0%",
            "pitch": "+0Hz"
        }
    }
    
    def __init__(self):
        self.current_approach = "shadow"
        logger.info("🔊 TTS Service inicializado (Edge TTS - Voz Masculina)")
    
    def set_approach(self, approach: str):
        """Define abordagem para ajustar voz."""
        if approach in self.VOICES:
            self.current_approach = approach
    
    async def synthesize(self, text: str, approach: str = None) -> bytes:
        """
        Converte texto em audio MP3.
        
        Args:
            text: Texto para sintetizar
            approach: Abordagem (define voz)
            
        Returns:
            bytes do audio MP3
        """
        if not text.strip():
            return b""
        
        if approach:
            self.current_approach = approach
        
        voice_config = self.VOICES.get(self.current_approach, self.VOICES["shadow"])
        
        try:
            logger.info(f"🎵 Sintetizando ({self.current_approach}): {text[:30]}...")
            
            # Criar comunicador Edge TTS
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice_config["voice"],
                rate=voice_config["rate"],
                pitch=voice_config["pitch"]
            )
            
            # Gerar audio em memoria
            audio_bytes = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_bytes += chunk["data"]
            
            logger.info(f"✅ Audio gerado: {len(audio_bytes)} bytes")
            return audio_bytes
            
        except Exception as e:
            logger.error(f"❌ Erro TTS: {e}")
            return b""
    
    def get_voice_for_approach(self, approach: str) -> dict:
        """Retorna config de voz para abordagem."""
        return self.VOICES.get(approach, self.VOICES["shadow"])
