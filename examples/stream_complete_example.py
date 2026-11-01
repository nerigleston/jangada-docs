"""Streaming com tools: o texto aparece enquanto o modelo escreve e, no fim,
vem a Completion completa (tool_calls, tokens e custo) — o laço de um agente.

Rode com:  ANTHROPIC_API_KEY=... python examples/stream_complete_example.py
"""
import asyncio

from jangada_ai import LLM, Message

ARQUIVOS: dict[str, str] = {}


def escrever_arquivo(caminho: str, conteudo: str) -> str:
    """Grava um arquivo do projeto."""
    ARQUIVOS[caminho] = conteudo
    return f"ok: {caminho} ({len(conteudo)} caracteres)"


async def main() -> None:
    llm = LLM("anthropic", "claude-haiku-5-5")
    historico: list[Message] = []
    pedido: str | None = "Crie README.md com uma linha de boas-vindas e explique o que fez."
    custo = 0.0
    for _ in range(4):  # rodadas do agente
        comp = None
        async for ev in llm.astream_complete(pedido, history=historico, tools=[escrever_arquivo]):
            if ev.type == "text":
                print(ev.text, end="", flush=True)
            else:
                comp = ev.completion
        custo += comp.cost or 0
        if pedido is not None:
            historico.append(Message("user", pedido))
            pedido = None
        if not comp.tool_calls:
            break
        historico.append(comp.assistant_message())
        historico.append(Message.tool_results(*[c.result(escrever_arquivo(**c.args)) for c in comp.tool_calls]))
    print(f"\n\narquivos: {list(ARQUIVOS)} · custo: US$ {custo:.5f}")


if __name__ == "__main__":
    asyncio.run(main())
