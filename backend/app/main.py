"""
PSICOVOZ - Main Application
Assistente Terapeutico por Voz em Tempo Real
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys

from config import settings

logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Iniciando PsicoVoz...")
    logger.info(f"📍 Whisper Model: {settings.WHISPER_MODEL}")
    logger.info(f"📍 TTS Model: {settings.TTS_MODEL}")
    yield
    logger.info("🛑 Encerrando PsicoVoz...")

app = FastAPI(
    title="PsicoVoz API",
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

@app.get("/")
async def root():
    return {
        "app": "PsicoVoz",
        "version": "0.1.0",
        "status": "online"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/approaches")
async def list_approaches():
    return {
        "approaches": [
            {"id": "psicanalise", "name": "Psicanalise", "icon": "🛋️"},
            {"id": "behaviorismo", "name": "Behaviorismo", "icon": "📊"},
            {"id": "gestalt", "name": "Gestalt", "icon": "🔮"}
        ]
    }

@app.websocket("/ws/voice/{approach}")
async def voice_conversation(websocket: WebSocket, approach: str):
    if approach not in ["psicanalise", "behaviorismo", "gestalt"]:
        await websocket.close(code=4001, reason="Abordagem invalida")
        return
    await websocket.accept()
    logger.info(f"🔌 Nova conexao - Abordagem: {approach}")
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        logger.info("🔌 Cliente desconectado")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
