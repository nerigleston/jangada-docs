"""Perfis por modelo: a MESMA chamada funciona em modelos com contratos diferentes.

Sem a camada de perfil, trocar gpt-4o -> gpt-5 ou gemini-2.5 -> gemini-3.5
quebraria (400 por temperature/max_tokens/thinking_budget). O jangada normaliza
o payload automaticamente conforme o modelo.
"""
from jangada_ai import LLM, Profile, register_profile

# gpt-4o aceita temperature; gpt-5 (raciocínio) NÃO — mesma chamada, sem erro.
for model in ["gpt-4o", "gpt-5.2"]:
    llm = LLM("openai", model, temperature=0.3, max_tokens=500)
    # internamente, no gpt-5.2: temperature é removido e max_tokens vira
    # max_completion_tokens. Você não precisa saber disso.
    print(model, "-> ok")

# gemini-2.5 aceita temperature; gemini-3.5 descarta sampling e usa thinking_level.
for model in ["gemini-2.5-flash", "gemini-3.5-flash"]:
    llm = LLM("gemini", model, temperature=0.5)
    print(model, "-> ok")

# Passar thinking_budget num modelo Gemini 3.x é convertido pra thinking_level
# (em vez de dar 400 por misturar os dois parâmetros legado/novo):
llm = LLM("gemini", "gemini-3.5-flash")
# llm.complete("...", thinking_budget=0)  # vira thinking_level="minimal"

# Registrar uma regra própria (ex.: um modelo novo que rejeita um parâmetro):
register_profile(
    "openai",
    r"^meu-modelo-custom",
    Profile(drop=("temperature",), rename={"max_tokens": "max_completion_tokens"}, note="custom"),
)

# IMPORTANTE (function calling multi-turn no Gemini 3.x): a API é estrita com
# thought signatures. Se você montar um loop de tools, passe o histórico
# COMPLETO e não modificado de volta (deixe o SDK cuidar), senão toma 400.
# O jangada não reconstrói histórico de tools, então structured output não
# esbarra nisso — mas vale a regra se você expandir para loops agênticos.
