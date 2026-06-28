"""Azure OpenAI: a mesma API da OpenAI, servida pela Azure.

O `model` é o NOME DO DEPLOYMENT (não o nome do modelo base). Config por env:
    AZURE_OPENAI_ENDPOINT=https://<seu-recurso>.openai.azure.com
    AZURE_OPENAI_API_KEY=...
    OPENAI_API_VERSION=2024-10-21   # opcional (tem default)

Instale: pip install "jangada-ai[openai]"
"""
from pydantic import BaseModel

from jangada_ai import LLM

# "meu-deploy-gpt4o" é o nome que você deu ao deployment no portal da Azure.
llm = LLM("azure", "meu-deploy-gpt4o")

# Texto — idêntico aos outros providers.
print(llm.complete("Explique {{tema}} em 1 frase.", tema="Azure OpenAI").text)


# Structured output (helper nativo .parse, igual à OpenAI).
class Pessoa(BaseModel):
    nome: str
    idade: int


p = llm.parse("Extraia: Ana, 28 anos.", Pessoa).parsed
print(p.nome, p.idade)
