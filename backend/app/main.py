"""
PSICOAPOIO - Main Application
Assistente Terapeutico por Voz em Tempo Real
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 50)
    logger.info("🧠 PSICOAPOIO - Iniciando...")
    logger.info("=" * 50)
    
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
    logger.info("🛑 PsicoApoio encerrado")


app = FastAPI(
    title="PsicoApoio API",
    description="Assistente Terapeutico por Voz em Tempo Real",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# FRONTEND - Servir HTML
# ============================================

@app.get("/app")
async def serve_frontend():
    """Serve a interface web."""
    frontend_path = Path("/app/frontend/web/index.html")
    if frontend_path.exists():
        return FileResponse(frontend_path)
    return {"error": "Frontend nao encontrado"}


# ============================================
# ENDPOINTS REST
# ============================================

@app.get("/")
async def root():
    return {
        "app": "PsicoApoio",
        "version": "0.1.0",
        "status": "online",
        "frontend": "/app",
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
    avatars = {
        "shadow": {"name": "Terapeuta", "image": "/avatars/shadow_avatar.png", "color": "#1a1a2e"},
        "psicanalise": {"name": "Dr. Sigmund", "image": "/avatars/freud_style.png", "color": "#4a3728"},
        "behaviorismo": {"name": "Dr. Burrhus", "image": "/avatars/skinner_style.png", "color": "#2d4a5e"},
        "gestalt": {"name": "Dr. Friedrich", "image": "/avatars/perls_style.png", "color": "#3d5a3d"}
    }
    return avatars.get(approach, avatars["shadow"])


# ============================================
# WEBSOCKET
# ============================================

@app.websocket("/ws/voice/{approach}")
async def voice_websocket(websocket: WebSocket, approach: str):
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
