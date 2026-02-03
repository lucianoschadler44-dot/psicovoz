"""
PSICOVOZ - Avatar Service
Usa SadTalker para animacao facial
"""
import os
import subprocess
import tempfile
import base64
from pathlib import Path
from loguru import logger


class AvatarService:
    """Servico de animacao de avatar usando SadTalker."""
    
    # Caminhos dos avatares
    AVATARS_DIR = Path("/app/avatars")
    
    AVATAR_IMAGES = {
        "shadow": "shadow_avatar.png",      # Silhueta inicial
        "psicanalise": "freud_style.png",   # Estilo Freud
        "behaviorismo": "skinner_style.png", # Estilo Skinner
        "gestalt": "perls_style.png"        # Estilo Perls
    }
    
    def __init__(self):
        self.sadtalker_path = os.getenv("SADTALKER_PATH", "/app/SadTalker")
        self.current_avatar = "shadow"
        logger.info("🎭 Avatar Service inicializado")
        
        # Verificar se SadTalker esta disponivel
        self._check_sadtalker()
    
    def _check_sadtalker(self):
        """Verifica se SadTalker esta instalado."""
        if os.path.exists(self.sadtalker_path):
            logger.info("✅ SadTalker encontrado")
            self.sadtalker_available = True
        else:
            logger.warning("⚠️ SadTalker nao encontrado - modo fallback")
            self.sadtalker_available = False
    
    def get_avatar_path(self, approach: str = None) -> Path:
        """Retorna caminho da imagem do avatar."""
        if approach is None:
            approach = self.current_avatar
        
        filename = self.AVATAR_IMAGES.get(approach, self.AVATAR_IMAGES["shadow"])
        return self.AVATARS_DIR / filename
    
    def set_approach(self, approach: str):
        """Define avatar baseado na abordagem escolhida."""
        if approach in self.AVATAR_IMAGES:
            self.current_avatar = approach
            logger.info(f"🎭 Avatar alterado para: {approach}")
        else:
            logger.warning(f"Abordagem desconhecida: {approach}")
    
    async def animate(self, audio_bytes: bytes, approach: str = None) -> bytes:
        """
        Anima avatar com audio.
        
        Args:
            audio_bytes: Audio WAV para sincronizar labios
            approach: Abordagem (determina qual avatar usar)
            
        Returns:
            bytes do video MP4 animado
        """
        if approach:
            self.set_approach(approach)
        
        if not self.sadtalker_available:
            return await self._fallback_animation(audio_bytes)
        
        try:
            return await self._sadtalker_animate(audio_bytes)
        except Exception as e:
            logger.error(f"❌ Erro SadTalker: {e}")
            return await self._fallback_animation(audio_bytes)
    
    async def _sadtalker_animate(self, audio_bytes: bytes) -> bytes:
        """Gera animacao usando SadTalker."""
        logger.info("🎬 Gerando animacao com SadTalker...")
        
        # Criar arquivos temporarios
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as audio_file:
            audio_file.write(audio_bytes)
            audio_path = audio_file.name
        
        output_dir = tempfile.mkdtemp()
        avatar_path = self.get_avatar_path()
        
        # Executar SadTalker
        cmd = [
            "python", f"{self.sadtalker_path}/inference.py",
            "--driven_audio", audio_path,
            "--source_image", str(avatar_path),
            "--result_dir", output_dir,
            "--enhancer", "gfpgan",
            "--still",
            "--preprocess", "crop"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=self.sadtalker_path
        )
        
        if result.returncode != 0:
            logger.error(f"SadTalker erro: {result.stderr}")
            raise Exception("SadTalker falhou")
        
        # Encontrar video gerado
        video_files = list(Path(output_dir).glob("*.mp4"))
        if not video_files:
            raise Exception("Nenhum video gerado")
        
        with open(video_files[0], "rb") as f:
            video_bytes = f.read()
        
        # Limpar temporarios
        os.unlink(audio_path)
        for f in Path(output_dir).iterdir():
            f.unlink()
        os.rmdir(output_dir)
        
        logger.info(f"✅ Video gerado: {len(video_bytes)} bytes")
        return video_bytes
    
    async def _fallback_animation(self, audio_bytes: bytes) -> bytes:
        """
        Fallback: retorna imagem estatica + audio.
        Frontend fara animacao simples (pulse/glow).
        """
        logger.info("🖼️ Usando fallback (imagem estatica)")
        
        avatar_path = self.get_avatar_path()
        
        # Retornar dados para frontend fazer animacao CSS
        if avatar_path.exists():
            with open(avatar_path, "rb") as f:
                image_bytes = f.read()
            
            return base64.b64encode(image_bytes)
        
        return b""
    
    def get_avatar_metadata(self, approach: str) -> dict:
        """Retorna metadados do avatar."""
        metadata = {
            "shadow": {
                "name": "Terapeuta",
                "description": "Escolha sua abordagem",
                "color": "#1a1a2e"
            },
            "psicanalise": {
                "name": "Dr. Sigmund",
                "description": "Abordagem Psicanalitica",
                "color": "#4a3728",
                "quote": "O sonho e a estrada real para o inconsciente"
            },
            "behaviorismo": {
                "name": "Dr. Burrhus",
                "description": "Abordagem Comportamental",
                "color": "#2d4a5e",
                "quote": "O comportamento e moldado por suas consequencias"
            },
            "gestalt": {
                "name": "Dr. Friedrich",
                "description": "Abordagem Gestalt",
                "color": "#3d5a3d",
                "quote": "Perca a cabeca e caia em si"
            }
        }
        return metadata.get(approach, metadata["shadow"])
