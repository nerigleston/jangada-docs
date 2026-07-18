"""RAG completo: indexar documentos e responder com contexto recuperado.

Requer: pip install "jangada-ai[rag,files]"  (embeddings via OpenAI/Gemini;
psycopg/pymongo para o vector store; pypdf/openpyxl/python-docx para os arquivos)
"""
import os

from jangada_ai import LLM
from jangada_ai.rag import RAG, vector_store

emb = LLM("openai", "text-embedding-3-small")   # ou ("gemini", "gemini-embedding-001")
chat = LLM("openai", "gpt-4o-mini")

# o store sai da STRING DE CONEXÃO (Postgres/pgvector ou MongoDB). "memory" p/ testar.
store = vector_store(os.environ.get("DATABASE_URL_VECTOR", "memory"))
rag = RAG(emb, store, chat=chat)

# 1) sincronizar com ID estável (reenvio idêntico gera zero embeddings novos)
rag.sync_document(
    "manual.pdf", name="manual.pdf", document_id="manual",
    metadata={"fonte": "manual"},
)
rag.add_texts(["A jangada troca de provider sem mudar o código."], metadatas=[{"fonte": "nota"}])

# 2) perguntar com busca híbrida (vetorial + texto, fundidos por RRF)
ans = rag.ask("Como troco de provider?", k=5, mode="hybrid")
print(ans.text)
print("\nFontes:")
for s in ans.sources:
    print(f"  {s.score:.3f}  {s.chunk.content[:80]}")
