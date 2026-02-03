# Sistema de Extensões - PsicoApoio

## Como adicionar conteúdo às personas

Para ADICIONAR conhecimento a qualquer psicólogo sem alterar o código principal:

1. Crie um arquivo na pasta `extensoes/` com o nome:
   - `freud_extra.py`
   - `lacan_extra.py`
   - `jung_extra.py`
   - `fritz_extra.py`
   - `laura_extra.py`
   - `zinker_extra.py`
   - `beck_extra.py`
   - `ellis_extra.py`
   - `judith_extra.py`

2. Use o formato:
```python
EXTRA = """
## NOVO CONTEÚDO ADICIONADO

Adicione aqui novos conceitos, técnicas, frases...
"""
```

3. O sistema automaticamente concatena ao prompt original.

## Exemplo de extensão

Arquivo: `freud_extra.py`
```python
EXTRA = """
## CASOS CLÍNICOS FAMOSOS

**Caso Dora (1905):**
- Histeria e transferência
- Sonhos como via de acesso

**Caso Hans (1909):**
- Fobia infantil
- Complexo de Édipo em ação
"""
```

## Regras
- NUNCA modifique os arquivos originais (freud.py, lacan.py, etc)
- APENAS crie arquivos *_extra.py nesta pasta
- O conteúdo é SOMADO, nunca substitui
