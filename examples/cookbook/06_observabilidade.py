"""Observabilidade automática (zero-config): nada de instrumentar o código.

Com o `.env` preenchido, a jangada envia um trace por chamada de LLM, sozinha e
em background, já com as capacidades detectadas (vision, documents, tools, mcp,
structured_output, guardrails). Para agrupar várias chamadas de uma request num
MESMO lote, use `observability_session` — cada chamada é enviada na hora, mas
todas compartilham o id do lote e o backend as agrupa.

Rode (com a plataforma da jangada configurada):
    pip install "jangada-ai[openai]"
    export OPENAI_API_KEY=sk-...
    export JANGADA_OBSERVABILITY=true
    export JANGADA_OBSERVABILITY_API_KEY=lobs_...      # token do projeto (dashboard)
    # opcional: export JANGADA_OBSERVABILITY_ENDPOINT=https://api.jangada.dev.br
    python examples/cookbook/06_observabilidade.py
"""
from __future__ import annotations

import os

from jangada_ai import LLM, observability_session

llm = LLM("openai", "gpt-4o-mini")
embedder = LLM("openai", "text-embedding-3-small")


def main() -> None:
    if os.environ.get("JANGADA_OBSERVABILITY", "").lower() not in {"1", "true", "yes", "on", "sim"}:
        print("Defina JANGADA_OBSERVABILITY=true e JANGADA_OBSERVABILITY_API_KEY para enviar traces.")

    # 1) Avulso: cada chamada vira um trace próprio (enviado sozinho).
    resumo = llm.complete("Escreva um parágrafo sobre jangadas nordestinas.")
    print(resumo.text)

    # 2) Agrupado: as duas chamadas entram no MESMO lote (mesmo trace id).
    with observability_session(name="resumo+revisão", user_id="cliente-123"):
        rascunho = llm.complete("Escreva um parágrafo sobre o mar.")
        llm.complete("Revise e melhore:\n{{texto}}", texto=rascunho.text)

    # 3) Embeddings também geram observations: uma ingestão só de embeddings
    # aparece no dashboard com latência, tokens, custo e capability "embeddings".
    with observability_session(name="rag.documents.ingest"):
        embedder.embed(["primeiro chunk", "segundo chunk"])

    print("\n[traces enviados automaticamente — completion e embeddings]")


if __name__ == "__main__":
    main()
