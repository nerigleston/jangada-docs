"""Retry com backoff + custo/tokens na resposta e agregado."""
from jangada_ai import LLM, Flow, register_price

# Retry no mesmo provider (backoff) antes de cair pro fallback.
llm = LLM(
    "groq", "llama-3.3-70b-versatile",
    max_retries=3, backoff_base=0.5, backoff_max=8.0, jitter=True,
    debug=True,
).with_fallback(
    LLM("openai", "gpt-5.2"),          # reserva se o primário esgotar
)

resp = llm.complete("Explique embeddings em 1 frase.")
print("respondido por:", resp.provider)
print("tokens:", resp.usage)            # {'input_tokens': ..., 'output_tokens': ...}
print("custo:  $", resp.cost)           # estimado em USD (None se modelo fora da tabela)

# Preços mudam — sobrescreva com os do seu contrato (USD por 1M tokens):
register_price(r"gpt-5\.2", 1.75, 14.00)

# Agregado num fluxo:
flow = (
    Flow(llm)
    .step("resumo", "Resuma:\n{{texto}}")
    .step("titulo", "Dê um título para:\n{{resumo}}")
)
r = flow.run(texto="...")
print("custo total do fluxo: $", r.cost)
print("tokens totais:", r.usage)
