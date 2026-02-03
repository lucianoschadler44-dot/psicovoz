"""
PSICOVOZ - Avatar Service (Mock para teste)
"""
from loguru import logger


class AvatarService:
    """Servico mock de avatar."""
    
    def __init__(self):
        logger.info("🎭 Avatar Service inicializado (modo teste)")
        self.current_avatar = "shadow"
    
    def set_approach(self, approach: str):
        self.current_avatar = approach
        logger.info(f"🎭 Avatar: {approach}")
    
    async def animate(self, audio_bytes: bytes, approach: str = None) -> bytes:
        """Mock: retorna dados vazios."""
        return b""
    
    def get_avatar_metadata(self, approach: str) -> dict:
        metadata = {
            "shadow": {"name": "Terapeuta", "color": "#1a1a2e"},
            "psicanalise": {"name": "Dr. Sigmund", "color": "#4a3728"},
            "behaviorismo": {"name": "Dr. Burrhus", "color": "#2d4a5e"},
            "gestalt": {"name": "Dr. Friedrich", "color": "#3d5a3d"}
        }
        return metadata.get(approach, metadata["shadow"])
