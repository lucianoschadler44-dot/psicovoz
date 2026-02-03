"""Prompts terapeuticos do PsicoVoz."""

PROMPTS = {
    "psicanalise": "psicanalise",
    "behaviorismo": "behaviorismo", 
    "gestalt": "gestalt"
}

def get_prompt(approach: str) -> str:
    from . import psicanalise, behaviorismo, gestalt
    prompts_map = {
        "psicanalise": psicanalise.PROMPT,
        "behaviorismo": behaviorismo.PROMPT,
        "gestalt": gestalt.PROMPT
    }
    return prompts_map.get(approach, psicanalise.PROMPT)
