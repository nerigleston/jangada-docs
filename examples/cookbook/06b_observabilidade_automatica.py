"""Observabilidade automática (zero-config): nada de instrumentar o código.

Com o `.env` preenchido, a jangada envia UM trace por chamada de LLM, sozinha e
em background, já com as capacidades detectadas (vision, documents, tools, mcp,
structured_output, guardrails). Compare com o modo manual em
`06_observabilidade_trace.py` (que agrupa N chamadas num lote).

Rode (com a plataforma da jangada configurada):
    pip install "jangada-ai[openai]"
    export OPENAI_API_KEY=sk-...
    export JANGADA_OBSERVABILITY=true
    export JANGADA_OBSERVABILITY_API_KEY=lobs_...      # token do projeto (dashboard)
    # opcional: export JANGADA_OBSERVABILITY_ENDPOINT=https://api.jangada.dev.br
    python examples/cookbook/06b_observabilidade_automatica.py
"""
from __future__ import annotations

import os

from jangada_ai import LLM

llm = LLM("openai", "gpt-4o-mini")


def main() -> None:
    if os.environ.get("JANGADA_OBSERVABILITY", "").lower() not in {"1", "true", "yes", "on", "sim"}:
        print("Defina JANGADA_OBSERVABILITY=true e JANGADA_OBSERVABILITY_API_KEY para enviar traces.")

    # Nenhuma instrumentação: cada chamada já é enviada à plataforma sozinha.
    resumo = llm.complete("Escreva um parágrafo sobre jangadas nordestinas.")
    print(resumo.text)

    # capability "structured_output" é detectada automaticamente em parse()
    # (e "tools"/"vision"/"documents"/"mcp" quando você passa tools/images/files/mcp_servers).
    print("\n[traces enviados automaticamente, um por chamada]")


if __name__ == "__main__":
    main()
