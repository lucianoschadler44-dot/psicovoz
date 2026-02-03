"""
PsicoApoio - Sistema de Prompts com Extensões
Carrega automaticamente prompts base + extensões
"""
import os
import importlib.util
from pathlib import Path

# Diretórios
BASE_DIR = Path(__file__).parent
EXTENSOES_DIR = BASE_DIR / "extensoes"

def _load_module(filepath):
    """Carrega módulo Python de um arquivo."""
    spec = importlib.util.spec_from_file_location("module", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def _load_prompt(linha, terapeuta):
    """Carrega prompt base + extensões."""
    # Carregar prompt base
    base_path = BASE_DIR / linha / f"{terapeuta}.py"
    if not base_path.exists():
        return None
    
    base_module = _load_module(base_path)
    prompt_attr = f"{terapeuta.upper()}_PROMPT"
    prompt = getattr(base_module, prompt_attr, "")
    
    # Carregar extensão se existir
    extra_path = EXTENSOES_DIR / f"{terapeuta}_extra.py"
    if extra_path.exists():
        extra_module = _load_module(extra_path)
        extra = getattr(extra_module, "EXTRA", "")
        prompt = prompt + "\n\n" + extra
    
    return prompt

# Mapeamento de terapeutas
TERAPEUTAS = {
    # Psicanálise
    "psicanalise_freud": ("psicanalise", "freud"),
    "psicanalise_lacan": ("psicanalise", "lacan"),
    "psicanalise_jung": ("psicanalise", "jung"),
    # Gestalt
    "gestalt_fritz": ("gestalt", "fritz"),
    "gestalt_laura": ("gestalt", "laura"),
    "gestalt_zinker": ("gestalt", "zinker"),
    # TCC
    "tcc_beck": ("tcc", "beck"),
    "tcc_ellis": ("tcc", "ellis"),
    "tcc_judith": ("tcc", "judith"),
}

# Compatibilidade com versão anterior
LEGACY_MAP = {
    "psicanalise": "psicanalise_freud",
    "gestalt": "gestalt_fritz",
    "behaviorismo": "tcc_beck",
    "tcc": "tcc_beck",
}

def get_prompt(approach: str) -> str:
    """Retorna o prompt para a abordagem/terapeuta especificado."""
    # Compatibilidade com versão anterior
    if approach in LEGACY_MAP:
        approach = LEGACY_MAP[approach]
    
    if approach not in TERAPEUTAS:
        # Fallback para Freud
        approach = "psicanalise_freud"
    
    linha, terapeuta = TERAPEUTAS[approach]
    prompt = _load_prompt(linha, terapeuta)
    
    if not prompt:
        return "Você é um assistente terapêutico de apoio psicológico."
    
    return prompt

def get_therapist_info(approach: str) -> dict:
    """Retorna informações do terapeuta."""
    INFO = {
        "psicanalise_freud": {
            "name": "Sigmund Freud",
            "title": "Pai da Psicanálise",
            "style": "Exploração do inconsciente, sonhos, livre associação"
        },
        "psicanalise_lacan": {
            "name": "Jacques Lacan",
            "title": "Psicanálise Estrutural",
            "style": "Linguagem, significantes, desejo do Outro"
        },
        "psicanalise_jung": {
            "name": "Carl Jung",
            "title": "Psicologia Analítica",
            "style": "Arquétipos, inconsciente coletivo, individuação"
        },
        "gestalt_fritz": {
            "name": "Fritz Perls",
            "title": "Fundador da Gestalt",
            "style": "Aqui-agora, confrontação, awareness corporal"
        },
        "gestalt_laura": {
            "name": "Laura Perls",
            "title": "Gestalt Relacional",
            "style": "Suporte, contato, presença acolhedora"
        },
        "gestalt_zinker": {
            "name": "Joseph Zinker",
            "title": "Gestalt Criativa",
            "style": "Experimentos artísticos, metáforas, criatividade"
        },
        "tcc_beck": {
            "name": "Aaron Beck",
            "title": "Pai da Terapia Cognitiva",
            "style": "Pensamentos automáticos, evidências, colaboração"
        },
        "tcc_ellis": {
            "name": "Albert Ellis",
            "title": "TREC - Terapia Racional Emotiva",
            "style": "Confrontação de crenças irracionais, modelo ABC"
        },
        "tcc_judith": {
            "name": "Judith Beck",
            "title": "TCC Contemporânea",
            "style": "Estruturada, didática, tarefas práticas"
        },
    }
    return INFO.get(approach, {"name": "Terapeuta", "title": "", "style": ""})
