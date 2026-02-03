"""
PSICOVOZ - Voice Handler
Orquestra conversa por voz em tempo real
"""
import asyncio
import json
import base64
from enum import Enum
from loguru import logger
from fastapi import WebSocket


class SessionState(Enum):
    """Estados da sessao."""
    INITIAL = "initial"           # Silhueta, aguardando escolha
    CHOOSING = "choosing"         # Usuario escolhendo abordagem
    ACTIVE = "active"             # Conversa ativa
    CRISIS = "crisis"             # Modo crise detectado
    ENDED = "ended"               # Sessao encerrada


class VoiceHandler:
    """Gerencia sessao de voz em tempo real."""
    
    WELCOME_MESSAGE = """Ola! Eu sou seu assistente de apoio psicologico.
Antes de comecarmos, voce tem preferencia por alguma linha da psicologia?
Pode ser psicanalise, behaviorismo ou gestalt.
Ou se preferir, posso escolher a mais adequada para voce."""
    
    def __init__(
        self,
        websocket: WebSocket,
        approach: str,
        stt_service,
        tts_service,
        llm_service,
        avatar_service=None
    ):
        self.ws = websocket
        self.approach = approach
        self.stt = stt_service
        self.tts = tts_service
        self.llm = llm_service
        self.avatar = avatar_service
        
        self.state = SessionState.INITIAL
        self.conversation_history = []
        self.user_context = ""
    
    async def run(self):
        """Loop principal da sessao."""
        logger.info(f"🎬 Iniciando sessao - Abordagem: {self.approach}")
        
        # Se abordagem ja definida, pular escolha
        if self.approach != "auto":
            self.state = SessionState.ACTIVE
            await self._send_welcome_with_approach()
        else:
            await self._send_initial_welcome()
        
        # Loop de mensagens
        while self.state != SessionState.ENDED:
            try:
                message = await self.ws.receive()
                
                if message["type"] == "websocket.disconnect":
                    break
                
                if "bytes" in message:
                    await self._handle_audio(message["bytes"])
                elif "text" in message:
                    await self._handle_text(json.loads(message["text"]))
                    
            except Exception as e:
                logger.error(f"❌ Erro no loop: {e}")
                break
        
        logger.info("🔚 Sessao encerrada")
    
    async def _send_initial_welcome(self):
        """Envia boas-vindas com silhueta."""
        self.state = SessionState.CHOOSING
        
        # Gerar audio de boas-vindas
        audio = await self.tts.synthesize(self.WELCOME_MESSAGE)
        
        # Enviar estado inicial
        await self._send_response(
            text=self.WELCOME_MESSAGE,
            audio=audio,
            avatar="shadow",
            state="choosing"
        )
    
    async def _send_welcome_with_approach(self):
        """Envia boas-vindas com avatar da abordagem."""
        metadata = self._get_avatar_metadata()
        
        welcome = f"""Ola! Eu sou {metadata['name']}, seu assistente com abordagem {metadata['description']}.
Estou aqui para te ouvir e apoiar. Como voce esta se sentindo hoje?"""
        
        audio = await self.tts.synthesize(welcome)
        
        await self._send_response(
            text=welcome,
            audio=audio,
            avatar=self.approach,
            state="active"
        )
        
        self.conversation_history.append({
            "role": "assistant",
            "content": welcome
        })
    
    async def _handle_audio(self, audio_bytes: bytes):
        """Processa audio recebido do usuario."""
        logger.info(f"🎤 Audio recebido: {len(audio_bytes)} bytes")
        
        # Transcrever audio
        result = await self.stt.transcribe(audio_bytes)
        text = result.get("text", "")
        
        if not text.strip():
            logger.warning("⚠️ Transcricao vazia")
            return
        
        # Enviar transcricao para o cliente
        await self.ws.send_json({
            "type": "transcription",
            "text": text
        })
        
        # Processar baseado no estado
        if self.state == SessionState.CHOOSING:
            await self._handle_approach_choice(text)
        else:
            await self._handle_conversation(text)
    
    async def _handle_text(self, data: dict):
        """Processa comandos de texto."""
        cmd = data.get("command")
        
        if cmd == "end_session":
            await self._end_session()
        elif cmd == "change_approach":
            new_approach = data.get("approach")
            if new_approach:
                await self._change_approach(new_approach)
        elif cmd == "text_message":
            text = data.get("text", "")
            if text:
                if self.state == SessionState.CHOOSING:
                    await self._handle_approach_choice(text)
                else:
                    await self._handle_conversation(text)
    
    async def _handle_approach_choice(self, text: str):
        """Processa escolha de abordagem."""
        choice = self.stt.detect_approach_choice(text)
        
        if choice == "auto":
            # LLM escolhe baseado no contexto
            self.user_context = text
            self.approach = await self.llm.select_approach_for_user(text)
            logger.info(f"🤖 LLM escolheu: {self.approach}")
        elif choice:
            self.approach = choice
        else:
            # Nao entendeu, pedir novamente
            msg = "Desculpe, nao entendi. Voce prefere psicanalise, behaviorismo ou gestalt?"
            audio = await self.tts.synthesize(msg)
            await self._send_response(text=msg, audio=audio, avatar="shadow", state="choosing")
            return
        
        # Mudar para estado ativo
        self.state = SessionState.ACTIVE
        await self._send_welcome_with_approach()
    
    async def _handle_conversation(self, text: str):
        """Processa mensagem na conversa ativa."""
        # Verificar crise
        crisis = await self.llm.detect_crisis(text)
        if crisis["is_crisis"]:
            self.state = SessionState.CRISIS
            await self._handle_crisis(crisis)
            return
        
        # Adicionar ao historico
        self.conversation_history.append({
            "role": "user",
            "content": text
        })
        
        # Gerar resposta
        response = await self.llm.chat(
            user_message=text,
            approach=self.approach,
            conversation_history=self.conversation_history
        )
        
        # Adicionar resposta ao historico
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        # Gerar audio
        audio = await self.tts.synthesize(response)
        
        # Enviar resposta
        await self._send_response(
            text=response,
            audio=audio,
            avatar=self.approach,
            state="active"
        )
    
    async def _handle_crisis(self, crisis: dict):
        """Responde a situacao de crise."""
        logger.warning("🚨 Modo CRISE ativado")
        
        response = crisis["response"]
        audio = await self.tts.synthesize(response)
        
        await self._send_response(
            text=response,
            audio=audio,
            avatar=self.approach,
            state="crisis",
            crisis_info={
                "cvv_phone": "188",
                "cvv_chat": "https://cvv.org.br",
                "type": crisis["type"]
            }
        )
        
        # Voltar ao estado ativo apos resposta de crise
        self.state = SessionState.ACTIVE
    
    async def _change_approach(self, new_approach: str):
        """Muda abordagem durante sessao."""
        if new_approach in ["psicanalise", "behaviorismo", "gestalt"]:
            self.approach = new_approach
            
            metadata = self._get_avatar_metadata()
            msg = f"Certo! Agora estou usando a abordagem {metadata['description']}."
            
            audio = await self.tts.synthesize(msg)
            await self._send_response(
                text=msg,
                audio=audio,
                avatar=new_approach,
                state="active"
            )
    
    async def _end_session(self):
        """Encerra sessao."""
        msg = "Foi bom conversar com voce. Lembre-se: buscar ajuda e um ato de coragem. Cuide-se!"
        audio = await self.tts.synthesize(msg)
        
        await self._send_response(
            text=msg,
            audio=audio,
            avatar=self.approach,
            state="ended"
        )
        
        self.state = SessionState.ENDED
    
    async def _send_response(
        self,
        text: str,
        audio: bytes,
        avatar: str,
        state: str,
        crisis_info: dict = None
    ):
        """Envia resposta completa para o cliente."""
        response = {
            "type": "response",
            "text": text,
            "audio": base64.b64encode(audio).decode() if audio else None,
            "avatar": avatar,
            "avatar_metadata": self._get_avatar_metadata(avatar),
            "state": state
        }
        
        if crisis_info:
            response["crisis_info"] = crisis_info
        
        await self.ws.send_json(response)
    
    def _get_avatar_metadata(self, approach: str = None) -> dict:
        """Retorna metadados do avatar."""
        if approach is None:
            approach = self.approach
            
        metadata = {
            "shadow": {
                "name": "Terapeuta",
                "description": "Escolha sua abordagem",
                "color": "#1a1a2e"
            },
            "psicanalise": {
                "name": "Dr. Sigmund",
                "description": "Psicanalitica",
                "color": "#4a3728"
            },
            "behaviorismo": {
                "name": "Dr. Burrhus",
                "description": "Comportamental",
                "color": "#2d4a5e"
            },
            "gestalt": {
                "name": "Dr. Friedrich",
                "description": "Gestalt",
                "color": "#3d5a3d"
            }
        }
        return metadata.get(approach, metadata["shadow"])
