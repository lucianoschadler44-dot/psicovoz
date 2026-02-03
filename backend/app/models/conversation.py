"""
PSICOVOZ - Modelos de Conversacao
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ApproachType(str, Enum):
    """Tipos de abordagem terapeutica."""
    PSICANALISE = "psicanalise"
    BEHAVIORISMO = "behaviorismo"
    GESTALT = "gestalt"
    AUTO = "auto"


class SessionState(str, Enum):
    """Estados da sessao."""
    INITIAL = "initial"
    CHOOSING = "choosing"
    ACTIVE = "active"
    CRISIS = "crisis"
    ENDED = "ended"


class Message(BaseModel):
    """Mensagem na conversa."""
    role: str = Field(..., description="user ou assistant")
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    audio_duration: Optional[float] = None


class Session(BaseModel):
    """Sessao de conversa."""
    id: str
    approach: ApproachType
    state: SessionState = SessionState.INITIAL
    messages: List[Message] = []
    created_at: datetime = Field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    crisis_detected: bool = False
    
    def add_message(self, role: str, content: str):
        self.messages.append(Message(role=role, content=content))
    
    def get_history(self, limit: int = 10) -> List[dict]:
        return [
            {"role": m.role, "content": m.content}
            for m in self.messages[-limit:]
        ]


class CrisisInfo(BaseModel):
    """Informacoes de crise."""
    is_crisis: bool = False
    crisis_type: Optional[str] = None
    cvv_phone: str = "188"
    cvv_chat: str = "https://cvv.org.br"


class AvatarMetadata(BaseModel):
    """Metadados do avatar."""
    name: str
    description: str
    color: str
    quote: Optional[str] = None


class WebSocketMessage(BaseModel):
    """Mensagem WebSocket."""
    type: str
    text: Optional[str] = None
    audio: Optional[str] = None  # base64
    avatar: Optional[str] = None
    avatar_metadata: Optional[AvatarMetadata] = None
    state: Optional[str] = None
    crisis_info: Optional[CrisisInfo] = None
