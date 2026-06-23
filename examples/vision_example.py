"""Vision: texto + imagem na mesma chamada, igual em todos os providers.

Passe imagens por caminho (str) ou via Image.from_bytes / from_base64.
A imagem vira o formato nativo de cada SDK automaticamente.
"""
from pydantic import BaseModel

from jangada_ai import LLM, Image


class Recibo(BaseModel):
    estabelecimento: str
    total: float


llm = LLM("gemini", "gemini-3.5-flash")  # ou "openai"/"anthropic"/"groq" (modelo com visão)

# 1) Caminho de arquivo direto
resp = llm.complete("O que aparece nesta imagem?", images=["foto.jpg"])
print(resp.text)

# 2) Bytes (ex.: upload no FastAPI) + structured output
with open("recibo.png", "rb") as f:
    img = Image.from_bytes(f.read(), "image/png")

recibo = llm.parse(
    "Extraia estabelecimento e total do recibo.",
    Recibo,
    images=[img],
).parsed
print(recibo.estabelecimento, recibo.total)
