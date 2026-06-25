"""Cache de respostas do LLM: exato e semântico.

Demonstra:
- ExactCache: 2ª chamada idêntica não bate no provider;
- SemanticCache: paráfrase da mesma pergunta acerta o cache (embeddings).

Rode com uma chave real (ex.: OPENAI_API_KEY).
"""
from jangada_ai import LLM, ExactCache, SemanticCache


def exato():
    llm = LLM("openai", "gpt-4o-mini", cache=ExactCache(ttl=3600))
    p = "Em uma frase, o que é entropia?"
    a = llm.complete(p)
    b = llm.complete(p)              # idêntico → cache hit (não chama o provider)
    print("exato:", a.text == b.text, "| custo 2ª:", b.cost)


def semantico():
    embedder = LLM("openai", "text-embedding-3-small")
    cache = SemanticCache(embedder, threshold=0.6)   # calibrado p/ embeddings OpenAI

    llm = LLM("openai", "gpt-4o-mini", cache=cache)
    llm.complete("Qual é a capital da França?")
    hit = llm.complete("Me diga a capital francesa, por favor.")  # paráfrase
    print("semântico:", hit.text)


if __name__ == "__main__":
    exato()
    semantico()
