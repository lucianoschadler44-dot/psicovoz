"""
PSICOVOZ - LLM Service
Usa Claude API (Anthropic)
"""
import anthropic
from loguru import logger
from config import settings
from prompts import get_prompt


class LLMService:
    """Servico de inteligencia usando Claude."""
    
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=settings.ANTHROPIC_API_KEY
        )
        self.model = settings.CLAUDE_MODEL
        self.max_tokens = settings.CLAUDE_MAX_TOKENS
        logger.info(f"🧠 LLM inicializado: {self.model}")
    
    async def chat(
        self,
        user_message: str,
        approach: str,
        conversation_history: list = None
    ) -> str:
        """
        Gera resposta terapeutica.
        
        Args:
            user_message: Mensagem do usuario
            approach: Abordagem terapeutica
            conversation_history: Historico da conversa
            
        Returns:
            Resposta do terapeuta
        """
        if conversation_history is None:
            conversation_history = []
        
        system_prompt = get_prompt(approach)
        
        # Montar mensagens
        messages = []
        for msg in conversation_history[-10:]:  # Ultimas 10 msgs
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        try:
            logger.info(f"💬 Enviando para Claude ({approach})")
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=messages
            )
            
            assistant_message = response.content[0].text
            logger.info(f"✅ Resposta: {assistant_message[:50]}...")
            
            return assistant_message
            
        except Exception as e:
            logger.error(f"❌ Erro LLM: {e}")
            return "Desculpe, tive um problema. Pode repetir?"
    
    async def detect_crisis(self, text: str) -> dict:
        """
        Detecta sinais de crise no texto.
        
        Returns:
            dict com 'is_crisis', 'type', 'response'
        """
        crisis_keywords = [
            "suicidio", "suicídio", "me matar", "quero morrer",
            "nao aguento mais", "não aguento mais", "acabar com tudo",
            "me machucar", "autolesao", "autolesão", "cortar"
        ]
        
        text_lower = text.lower()
        
        for keyword in crisis_keywords:
            if keyword in text_lower:
                logger.warning(f"⚠️ CRISE DETECTADA: {keyword}")
                return {
                    "is_crisis": True,
                    "type": "suicidal_ideation",
                    "response": self._get_crisis_response()
                }
        
        return {"is_crisis": False, "type": None, "response": None}
    
    def _get_crisis_response(self) -> str:
        """Resposta padrao para crise."""
        return """Eu percebo que voce esta passando por um momento muito dificil, 
e quero que saiba que sua vida tem valor. 

Por favor, ligue agora para o CVV no 188. 
Funciona 24 horas e a ligacao e gratuita.

Voce tambem pode conversar pelo chat em cvv.org.br.

Estou aqui com voce. Voce nao esta sozinho."""
    
    async def select_approach_for_user(self, user_context: str) -> str:
        """
        Seleciona abordagem automaticamente baseado no contexto.
        
        Returns:
            'psicanalise', 'behaviorismo' ou 'gestalt'
        """
        prompt = f"""Baseado no seguinte contexto do usuario, escolha a abordagem 
terapeutica mais adequada. Responda APENAS com uma palavra: 
psicanalise, behaviorismo ou gestalt.

Contexto: {user_context}

Criterios:
- psicanalise: questoes de infancia, relacionamentos, padroes repetitivos
- behaviorismo: ansiedade, fobias, metas praticas, mudanca de habitos
- gestalt: autoconhecimento, momento presente, emocoes no corpo
"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=20,
                messages=[{"role": "user", "content": prompt}]
            )
            
            choice = response.content[0].text.strip().lower()
            
            if choice in ["psicanalise", "behaviorismo", "gestalt"]:
                return choice
            return "psicanalise"  # Default
            
        except Exception as e:
            logger.error(f"Erro ao selecionar abordagem: {e}")
            return "psicanalise"
