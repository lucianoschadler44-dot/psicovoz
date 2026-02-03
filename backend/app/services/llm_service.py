"""
PSICOAPOIO - LLM Service
Usa Claude API com prompts específicos por terapeuta
"""
import anthropic
from loguru import logger
from config import settings
from prompts import get_prompt


class LLMService:
    """Serviço de LLM usando Claude."""
    
    CRISIS_KEYWORDS = [
        "suicid", "me matar", "acabar com tudo", "não aguento mais",
        "quero morrer", "vontade de morrer", "sem saída", "desistir de viver",
        "automutilação", "me machucar", "me cortar"
    ]
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.CLAUDE_MODEL
        logger.info(f"🧠 LLM inicializado: {self.model}")
    
    async def chat(self, user_message: str, approach: str, conversation_history: list) -> str:
        """Gera resposta terapêutica."""
        try:
            system_prompt = get_prompt(approach)
            
            messages = []
            for msg in conversation_history[-10:]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            if not messages or messages[-1]["role"] != "user":
                messages.append({"role": "user", "content": user_message})
            
            logger.info(f"💬 Enviando para Claude ({approach})")
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=settings.CLAUDE_MAX_TOKENS,
                system=system_prompt,
                messages=messages
            )
            
            text = response.content[0].text
            logger.info(f"✅ Resposta: {text[:50]}...")
            return text
            
        except Exception as e:
            logger.error(f"❌ Erro LLM: {e}")
            return "Desculpe, tive um problema. Pode repetir?"
    
    async def detect_crisis(self, text: str) -> dict:
        """Detecta menções a crise/suicídio."""
        text_lower = text.lower()
        
        for keyword in self.CRISIS_KEYWORDS:
            if keyword in text_lower:
                logger.warning(f"🚨 Crise detectada: {keyword}")
                return {
                    "is_crisis": True,
                    "response": """Percebo que você está passando por um momento muito difícil. 
Quero que saiba que você não está sozinho e que existem pessoas prontas para ajudar.

Se você está pensando em se machucar, por favor ligue agora para o CVV:
📞 188 (24 horas, gratuito)
💬 www.cvv.org.br (chat)

Sua vida tem valor. Posso continuar aqui com você, mas é importante buscar ajuda profissional também."""
                }
        
        return {"is_crisis": False, "response": ""}
    
    async def select_approach_for_user(self, user_input: str) -> str:
        """Seleciona abordagem baseada no contexto."""
        return "psicanalise_freud"
