"""DeepSeek: chat.completions num base_url próprio (mesma receita do OpenRouter).

Config por env:
    DEEPSEEK_API_KEY=...

Instale: pip install "jangada-ai[openai]"
"""
from pydantic import BaseModel

from jangada_ai import LLM

llm = LLM("deepseek", "deepseek-v4-flash")

# Texto — idêntico aos outros providers.
print(llm.complete("Explique {{tema}} em 1 frase.", tema="DeepSeek").text)


# Structured output — sem JSON Schema estrito, a jangada usa JSON Object mode
# por baixo dos panos (schema injetado como instrução).
class Pessoa(BaseModel):
    nome: str
    idade: int


p = llm.parse("Extraia: Ana, 28 anos.", Pessoa).parsed
print(p.nome, p.idade)


# Modo thinking (raciocínio) — só em deepseek-v4-pro/-flash. `thinking` vai por
# `extra=`; a jangada empacota em `extra_body` sozinha (o SDK oficial da OpenAI
# não reconhece o campo, precisa desse caminho). Nesse modo a API rejeita
# temperature/top_p/presence_penalty/frequency_penalty — não passe junto.
pro = LLM("deepseek", "deepseek-v4-pro")
comp = pro.complete(
    "Se 3 maçãs custam R$ 6, quanto custam 7 maçãs? Responda só o número.",
    extra={"thinking": {"type": "enabled", "reasoning_effort": "high"}},
)
print(comp.text)
