"""Fallback por erro: troca de modelo/provider conforme o tipo de erro da API.

Por padrão, faz failover em: rate limit (429), timeout, erro de conexão,
5xx (incl. overloaded 529) e 404 (modelo inexistente). NÃO faz failover em
auth (401/403) nem bad request (400/422), porque trocar de provider não
resolveria esses casos — esse comportamento é configurável via retry_on.
"""
from jangada_ai import LLM
from jangada_ai.errors import RateLimitError, ServerError

# Primário rápido e barato; se estourar, cai pro OpenAI; por fim, Claude.
llm = LLM("groq", "llama-3.3-70b-versatile").with_fallback(
    LLM("openai", "gpt-5.2"),
    LLM("anthropic", "claude-opus-4-8"),
)

resp = llm.complete("Explique embeddings em 1 frase.")
print(f"respondido por: {resp.provider}")
print(resp.text)

# Fallback só de MODELO dentro do mesmo provider:
so_modelo = LLM("openai", "gpt-5.2").with_fallback(LLM("openai", "gpt-5-mini"))

# Customizar quais erros disparam failover (ex.: só rate limit e 5xx):
restrito = LLM(
    "groq",
    "llama-3.3-70b-versatile",
    retry_on=(RateLimitError, ServerError),
).with_fallback(LLM("anthropic", "claude-opus-4-8"))

# Tudo isso vale igual no async (acomplete) e no streaming (stream/astream),
# onde o failover acontece antes do primeiro token.
