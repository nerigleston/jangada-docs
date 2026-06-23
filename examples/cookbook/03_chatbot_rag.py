"""Chatbot RAG: indexa textos e responde com base neles (busca híbrida).

Caso real: uma base de conhecimento (FAQ, docs internos) e perguntas em
linguagem natural. A jangada faz embeddings + busca **híbrida** (BM25 lexical +
vetorial, fundidos por RRF) e responde citando o contexto. Aqui usamos o store
em memória (sem banco); troque por `vector_store("postgresql://...")` em produção.

Rode:
    pip install "jangada-ai[openai,rag]"
    export OPENAI_API_KEY=sk-...
    python examples/cookbook/03_chatbot_rag.py
"""
from __future__ import annotations

from jangada_ai import LLM
from jangada_ai.rag import RAG, InMemoryVectorStore

BASE = [
    "A jangada é uma camada fina sobre os SDKs de LLM (Anthropic, OpenAI, Groq, Gemini).",
    "Para trocar de provider basta mudar LLM('provider', 'modelo') — o resto do código não muda.",
    "O fallback tenta outro modelo/provider quando o primeiro falha por rate limit, 5xx ou timeout.",
    "A busca híbrida do RAG combina BM25 (palavras) e vetorial (semântica) por Reciprocal Rank Fusion.",
    "Structured output devolve um objeto Pydantic validado com uma só chamada parse().",
]


def main() -> None:
    embedder = LLM("openai", "text-embedding-3-small")
    chat = LLM("openai", "gpt-4o-mini")

    rag = RAG(embedder, InMemoryVectorStore(), chat=chat, k=3, alpha=0.5)
    rag.add_texts(BASE)

    for pergunta in [
        "Como troco de provider sem reescrever o código?",
        "Quando o fallback é acionado?",
        "O que é a busca híbrida?",
    ]:
        resp = rag.ask(pergunta)
        print(f"\nP: {pergunta}\nR: {resp.text}")
        print(f"   (fontes: {len(resp.sources)} trechos)")


if __name__ == "__main__":
    main()
