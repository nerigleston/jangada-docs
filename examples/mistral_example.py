"""Mistral via SDK oficial (mistralai): texto, structured, streaming, tools e embeddings.

Chave: env MISTRAL_API_KEY (ou api_key= no construtor). O `model` é o id da
Mistral (ex.: mistral-large-latest, mistral-small-latest, mistral-medium-latest).

Instale: pip install "jangada-ai[mistral]"
"""
import asyncio

from pydantic import BaseModel

from jangada_ai import LLM

llm = LLM("mistral", "mistral-large-latest")

# Texto.
print(llm.complete("Diga olá em português, só uma palavra.").text)

# Streaming.
for pedaco in llm.stream("Conte de 1 a 5 separado por vírgula."):
    print(pedaco, end="", flush=True)
print()


# Structured output (helper nativo chat.parse — aceita o modelo Pydantic direto).
class Fatura(BaseModel):
    fornecedor: str
    total: float


f = llm.parse("Extraia: Padaria do Zé, total R$26.", Fatura).parsed
print(f.fornecedor, f.total)


# Function calling.
def clima(cidade: str) -> str:
    """Retorna o clima atual da cidade."""
    return f"Ensolarado em {cidade}"


comp = llm.complete("Como está o clima em Recife?", tools=[clima], tool_choice="auto")
for call in comp.tool_calls:
    print(call.name, call.args)

# Embeddings (mistral-embed).
emb = LLM("mistral", "mistral-embed")
vec = emb.embed("jangada é uma camada fina sobre os SDKs de LLM")
print("dim:", len(vec))

# OCR / Document AI (mistral-ocr-latest): URL, caminho, bytes ou ImagePart.
ocr = LLM("mistral", "mistral-ocr-latest")
doc = ocr.ocr("https://arxiv.org/pdf/2310.06825.pdf")
print("páginas:", len(doc.pages))
print(doc.pages[0].markdown[:200])

# Transcrição de áudio (Voxtral).
stt = LLM("mistral", "voxtral-mini-latest")
# print(stt.transcribe("audio.mp3", language="pt").text)


# Async.
async def main():
    print((await llm.acomplete("Responda apenas: ok")).text)


asyncio.run(main())
