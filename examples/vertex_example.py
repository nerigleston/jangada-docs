"""Vertex AI (Google Cloud): Gemini com a mesma API, mas via projeto GCP.

Em vez de API key, usa ADC (Application Default Credentials) + project/location.
Autentique com:
    gcloud auth application-default login
e configure:
    GOOGLE_CLOUD_PROJECT=meu-projeto
    GOOGLE_CLOUD_LOCATION=us-central1   # opcional (default us-central1)
(ou passe project=/location= no construtor).

Instale: pip install "jangada-ai[gemini]"
"""
from pydantic import BaseModel

from jangada_ai import LLM

llm = LLM("vertex", "gemini-2.5-flash")  # project/location vêm do ambiente

# Texto — mesma API do provider "gemini".
print(llm.complete("Explique {{tema}} em 1 frase.", tema="Vertex AI").text)


# Structured output (response_schema nativo do Gemini).
class Produto(BaseModel):
    nome: str
    preco: float


p = llm.parse("Extraia: Caneta, R$8.", Produto).parsed
print(p.nome, p.preco)
