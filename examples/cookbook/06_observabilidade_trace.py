"""Observabilidade: agrupa as chamadas de uma request num lote (trace).

Caso real: uma request da sua app faz várias chamadas de IA; você quer ver todas
juntas (tokens, custo, latência, status) na plataforma de observability. Cada
chamada vira uma `observation` do mesmo `trace` (o "lote"). O `Trace` é um
context manager — no fim, envia tudo de uma vez (flush).

Rode (com a plataforma da jangada configurada):
    pip install "jangada-ai[openai]"
    export OPENAI_API_KEY=sk-...
    export LOBS_API_KEY=lobs_...  LOBS_ENDPOINT=https://api.suaplataforma.com
    python examples/cookbook/06_observabilidade_trace.py
"""
from __future__ import annotations

import os

from jangada_ai import LLM
from jangada_ai.observability import Observability

llm = LLM("openai", "gpt-4o-mini")


def main() -> None:
    endpoint = os.environ.get("LOBS_ENDPOINT")
    api_key = os.environ.get("LOBS_API_KEY")
    if not (endpoint and api_key):
        print("Defina LOBS_ENDPOINT e LOBS_API_KEY (token do projeto no dashboard).")
        return

    obs = Observability(api_key=api_key, endpoint=endpoint)

    # um lote = uma request da sua app; cada complete() vira uma observation
    with obs.trace(name="resumo-artigo", user_id="cliente-123") as trace:
        rascunho = llm.complete("Escreva um parágrafo sobre jangadas nordestinas.")
        trace.log(rascunho, name="rascunho")

        revisao = llm.complete("Revise e melhore:\n{{texto}}", texto=rascunho.text)
        trace.log(revisao, name="revisão")

        print(revisao.text)
    # ao sair do "with", o lote é enviado (flush) com as 2 observations
    print("\n[lote enviado para a plataforma de observability]")


if __name__ == "__main__":
    main()
