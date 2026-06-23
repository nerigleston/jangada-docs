"""Structured output: a mesma chamada parse() funciona em qualquer provider.

Por baixo: OpenAI usa .parse(), Groq usa response_format json_schema,
Gemini usa response_schema e Anthropic usa tool-forcing. Você não precisa saber.
"""
from pydantic import BaseModel, Field

from jangada_ai import LLM


class Fatura(BaseModel):
    fornecedor: str
    total: float = Field(description="Valor total em reais")
    itens: list[str]


texto = "Padaria do Zé — Pão R$8, Leite R$6, Café R$12. Total R$26."

for provider, model in [
    ("openai", "gpt-5.2"),
    ("groq", "llama-3.3-70b-versatile"),
    ("gemini", "gemini-3.5-flash"),
    ("anthropic", "claude-opus-4-8"),
]:
    llm = LLM(provider, model)
    fatura = llm.parse("Extraia a fatura:\n{{texto}}", Fatura, texto=texto).parsed
    print(provider, "->", fatura.fornecedor, fatura.total, fatura.itens)
