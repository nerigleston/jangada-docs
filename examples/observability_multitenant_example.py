"""Observabilidade multi-tenant: uma chave de projeto por empresa no mesmo processo.

Cada `observability_session(api_key=...)` manda as chamadas de dentro do `with`
para o projeto daquela chave — sem `JANGADA_OBSERVABILITY` no ambiente e sem
misturar empresas, mesmo com requests concorrentes.

Rode com:  OPENAI_API_KEY=... OBS_KEY_A=lobs_... OBS_KEY_B=lobs_... \\
           python examples/observability_multitenant_example.py
"""
import asyncio
import os

from jangada_ai import LLM, flush_observability, observability_session

EMPRESAS = {
    "padaria": os.environ.get("OBS_KEY_A", "lobs_empresa_a"),
    "oficina": os.environ.get("OBS_KEY_B", "lobs_empresa_b"),
}

llm = LLM("openai", "gpt-4o-mini")


async def atender(empresa: str, usuario: str, pergunta: str) -> str:
    with observability_session(
        api_key=EMPRESAS[empresa],      # o trace vai para o projeto desta empresa
        name=f"atendimento-{empresa}",
        user_id=usuario,
    ):
        resp = await llm.acomplete(pergunta)
        return resp.text


async def main() -> None:
    respostas = await asyncio.gather(
        atender("padaria", "ana", "Sugira um nome para um pão de fermentação natural."),
        atender("oficina", "bia", "Liste 3 itens de revisão antes de uma viagem."),
    )
    for r in respostas:
        print("-", r[:120])
    flush_observability()  # não perca os últimos traces ao sair


if __name__ == "__main__":
    asyncio.run(main())
