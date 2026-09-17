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
        print(ans.text, ans.iterations, ans.tool_trace)


def veta_tools_perigosas(call):
    return call.name != "apagar_arquivo"   # False = veta a chamada


async def agente_mcp_com_controle():
    """allowed_tools restringe o que o modelo vê; on_tool_call/on_tool_result
    auditam/vetam cada chamada; keep_alive reconecta sozinho se cair."""
    g = LLM("openai", "gpt-4o-mini")
    mcp = MCPClient("https://meu-mcp/mcp/", auth_token="TOKEN", keep_alive=True)
    ans = await run_agent(
        g, "Liste e depois apague os temporários", client=mcp,
        allowed_tools=["listar_arquivos", "apagar_arquivo"],
        on_tool_call=veta_tools_perigosas,
        on_tool_result=lambda c, r: print(c.name, "->", r.is_error),
    )
    print(ans.text)
    await mcp.aclose()


# asyncio.run(agente_mcp())
# asyncio.run(agente_mcp_com_controle())
