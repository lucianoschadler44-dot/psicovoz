"""
PSICOVOZ - Voice Handler (modo texto)
"""
import json
import base64
from enum import Enum
from loguru import logger
from fastapi import WebSocket


class SessionState(Enum):
    ACTIVE = "active"
    CRISIS = "crisis"
    ENDED = "ended"


class VoiceHandler:
    def __init__(self, websocket, approach, stt_service, tts_service, llm_service, avatar_service=None):
        self.ws = websocket
        self.approach = approach
        self.stt = stt_service
        self.tts = tts_service
        self.llm = llm_service
        self.state = SessionState.ACTIVE
        self.conversation_history = []
    
    async def run(self):
        logger.info(f"🎬 Sessão iniciada - Abordagem: {self.approach}")
        await self._send_welcome()
        
        while self.state != SessionState.ENDED:
            try:
                message = await self.ws.receive()
                if message["type"] == "websocket.disconnect":
                    break
                if "text" in message:
                    data = json.loads(message["text"])
                    if data.get("command") == "text_message":
                        await self._handle_conversation(data.get("text", ""))
            except Exception as e:
                logger.error(f"❌ Erro: {e}")
                break
        
        logger.info("🔚 Sessão encerrada")
    
    async def _send_welcome(self):
        names = {"psicanalise": "Dr. Sigmund", "behaviorismo": "Dr. Aaron", "gestalt": "Dr. Fritz"}
        name = names.get(self.approach, "Terapeuta")
        welcome = f"Olá! Eu sou {name}, seu assistente terapêutico. Estou aqui para te ouvir e apoiar. Como você está se sentindo hoje?"
        
        await self._send_response(welcome)
        self.conversation_history.append({"role": "assistant", "content": welcome})
    
    async def _handle_conversation(self, text: str):
        if not text.strip():
            return
        
        crisis = await self.llm.detect_crisis(text)
        if crisis["is_crisis"]:
            await self._send_response(crisis["response"], crisis_info=True)
            return
        
        self.conversation_history.append({"role": "user", "content": text})
        
        response = await self.llm.chat(
            user_message=text,
            approach=self.approach,
            conversation_history=self.conversation_history
        )
        
        self.conversation_history.append({"role": "assistant", "content": response})
        await self._send_response(response)
    
    async def _send_response(self, text, crisis_info=False):
        response = {"type": "response", "text": text, "avatar": self.approach}
        if crisis_info:
            response["crisis_info"] = {"cvv_phone": "188"}
        await self.ws.send_json(response)
