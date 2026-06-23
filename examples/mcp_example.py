"""MCP (Model Context Protocol): nativo (server-side) e agente client-side.

- Nativo remoto (Anthropic/OpenAI/Groq): o provider conecta e executa as tools.
- Agente client-side (qualquer provider): MCPClient + run_agent conectam no
  servidor, listam as tools e rodam o loop sozinhos. Requer: jangada-ai[mcp].
"""
import asyncio

from jangada_ai import LLM, MCPClient, MCPServer, run_agent

# --- nativo remoto por URL (server-side) ---
llm = LLM("anthropic", "claude-opus-4-8")   # ou ("openai", "gpt-4o"), ("groq", ...)
comp = llm.complete(
    "Liste as issues abertas.",
    mcp_servers=[MCPServer(url="https://mcp.exemplo.com/sse", name="github",
                           authorization_token="TOKEN", allowed_tools=["list_issues"])],
)
print(comp.text)


# --- agente MCP client-side (funciona em QUALQUER provider) ---
async def agente_mcp():
    g = LLM("openai", "gpt-4o-mini")   # ou anthropic/groq/gemini
    async with MCPClient("https://meu-mcp/mcp/") as mcp:        # ou command=/args= (stdio)
        ans = await run_agent(g, "Role uns dados", client=mcp)
        print(ans.text)


# asyncio.run(agente_mcp())
