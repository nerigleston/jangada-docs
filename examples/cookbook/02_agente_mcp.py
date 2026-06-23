"""Agente MCP: o LLM conecta num servidor MCP real e usa as tools sozinho.

Caso real: você tem um servidor MCP (ex.: um ERP exposto via MCP) e quer
perguntar em português — o modelo decide qual tool chamar, a jangada executa e
reenvia, até a resposta final. Provider-agnóstico (funciona nos 4).

Rode:
    pip install "jangada-ai[openai,mcp]"
    export OPENAI_API_KEY=sk-...
    python examples/cookbook/02_agente_mcp.py https://seu-mcp/mcp/ "Quais os dados da empresa?"
"""
from __future__ import annotations

import asyncio
import sys

from jangada_ai import LLM
from jangada_ai.mcp import MCPClient, run_agent


async def main(url: str, pergunta: str) -> None:
    llm = LLM("openai", "gpt-4o-mini")

    async with MCPClient(url) as mcp:  # ou MCPClient(command="python", args=["server.py"]) p/ stdio
        tools = await mcp.list_tools()
        print(f"Conectado: {len(tools)} tools disponíveis.\n")

        comp = await run_agent(llm, pergunta, client=mcp, max_iterations=8)
        print(comp.text)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('uso: python 02_agente_mcp.py <url_mcp> "<pergunta>"')
        sys.exit(1)
    asyncio.run(main(sys.argv[1], sys.argv[2]))
