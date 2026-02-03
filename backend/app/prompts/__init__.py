"""Prompts terapêuticos do PsicoVoz."""
from .psicanalise import PROMPT as PSICANALISE_PROMPT
from .behaviorismo import PROMPT as BEHAVIORISMO_PROMPT
from .gestalt import PROMPT as GESTALT_PROMPT

PROMPTS = {
    "psicanalise": PSICANALISE_PROMPT,
    "behaviorismo": BEHAVIORISMO_PROMPT,
    "gestalt": GESTALT_PROMPT
}

def get_prompt(approach: str) -> str:
    """Retorna o prompt para a abordagem especificada."""
    return PROMPTS.get(approach, PSICANALISE_PROMPT)
