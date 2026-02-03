"""
PSICOVOZ - Main Application
Assistente Terapeutico por Voz em Tempo Real
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from loguru import logger
from pathlib import Path
import sys

from config import settings
from services.stt_service import STTService
from services.tts_service import TTSService
from services.llm_service import LLMService
from services.avatar_service import AvatarService
from websocket.voice_handler import VoiceHandler

# Configurar logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializacao e shutdown."""
    logger.info("=" * 50)
    logger.info("🧠 PSICOVOZ - Iniciando...")
    logger.info("=" * 50)
    
    # Inicializar servicos
    try:
        app.state.stt = STTService()
        app.state.tts = TTSService()
        app.state.llm = LLMService()
        app.state.avatar = AvatarService()
        logger.info("✅ Todos os servicos inicializados")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar servicos: {e}")
        raise
    
    yield
    
    logger.info("🛑 PsicoVoz encerrado")


app = FastAPI(
    title="PsicoVoz API",
    description="Assistente Terapeutico por Voz em Tempo Real",
    version="0.1.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir avatares estaticos
avatars_path = Path("/app/avatars")
if avatars_path.exists():
    app.mount("/avatars", StaticFiles(directory=str(avatars_path)), name="avatars")


# ============================================
# ENDPOINTS REST
# ============================================

@app.get("/")
async def root():
    return {
        "app": "PsicoVoz",
        "version": "0.1.0",
        "status": "online",
        "endpoints": {
            "health": "/health",
            "approaches": "/api/approaches",
            "websocket": "/ws/voice/{approach}"
        }
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "services": {
            "stt": "ready",
            "tts": "ready",
            "llm": "ready",
            "avatar": "ready"
        }
    }


@app.get("/api/approaches")
async def list_approaches():
    return {
        "approaches": [
            {
                "id": "auto",
                "name": "Deixar o sistema escolher",
                "description": "O assistente escolhe a melhor abordagem para voce",
                "icon": "🎯",
                "avatar": "shadow"
            },
            {
                "id": "psicanalise",
                "name": "Psicanalise",
                "description": "Foco no inconsciente, sonhos e historia pessoal",
                "icon": "🛋️",
                "avatar": "freud_style",
                "therapist": "Dr. Sigmund"
            },
            {
                "id": "behaviorismo",
                "name": "Behaviorismo (TCC)",
                "description": "Foco em comportamentos, pensamentos e metas praticas",
                "icon": "📊",
                "avatar": "skinner_style",
                "therapist": "Dr. Burrhus"
            },
            {
                "id": "gestalt",
                "name": "Gestalt",
                "description": "Foco no aqui-agora, sensacoes e experiencia presente",
                "icon": "🔮",
                "avatar": "perls_style",
                "therapist": "Dr. Friedrich"
            }
        ]
    }


@app.get("/api/avatar/{approach}")
async def get_avatar_info(approach: str):
    """Retorna informacoes do avatar."""
    avatars = {
        "shadow": {
            "name": "Terapeuta",
            "image": "/avatars/shadow_avatar.png",
            "color": "#1a1a2e",
            "description": "Escolha sua abordagem"
        },
        "psicanalise": {
            "name": "Dr. Sigmund",
            "image": "/avatars/freud_style.png",
            "color": "#4a3728",
            "quote": "O sonho e a estrada real para o inconsciente"
        },
        "behaviorismo": {
            "name": "Dr. Burrhus",
            "image": "/avatars/skinner_style.png",
            "color": "#2d4a5e",
            "quote": "O comportamento e moldado por suas consequencias"
        },
        "gestalt": {
            "name": "Dr. Friedrich",
            "image": "/avatars/perls_style.png",
            "color": "#3d5a3d",
            "quote": "Perca a cabeca e caia em si"
        }
    }
    return avatars.get(approach, avatars["shadow"])


# ============================================
# WEBSOCKET
# ============================================

@app.websocket("/ws/voice/{approach}")
async def voice_websocket(websocket: WebSocket, approach: str):
    """WebSocket para conversa por voz."""
    valid = ["auto", "psicanalise", "behaviorismo", "gestalt"]
    
    if approach not in valid:
        await websocket.close(code=4001, reason="Abordagem invalida")
        return
    
    await websocket.accept()
    logger.info(f"🔌 Conexao WebSocket - Abordagem: {approach}")
    
    handler = VoiceHandler(
        websocket=websocket,
        approach=approach,
        stt_service=app.state.stt,
        tts_service=app.state.tts,
        llm_service=app.state.llm,
        avatar_service=app.state.avatar
    )
    
    try:
        await handler.run()
    except WebSocketDisconnect:
        logger.info("🔌 Cliente desconectado")
    except Exception as e:
        logger.error(f"❌ Erro WebSocket: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
