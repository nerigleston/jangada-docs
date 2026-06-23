"""MCP (Model Context Protocol): remoto por URL e client-side (Gemini, async).

Remoto (Anthropic/OpenAI/Groq): o provider conecta no servidor MCP e executa
as tools. Gemini: sessão client-side via acomplete (a sessão é assíncrona).
"""
import asyncio

from jangada_ai import LLM, MCPServer

# --- remoto por URL (server-side) ---
llm = LLM("anthropic", "claude-opus-4-8")   # ou ("openai", "gpt-4o"), ("groq", ...)
comp = llm.complete(
    "Liste as issues abertas.",
    mcp_servers=[MCPServer(
        url="https://mcp.exemplo.com/sse",
        name="github",
        authorization_token="TOKEN",      # opcional
        allowed_tools=["list_issues"],    # opcional
    )],
)
print(comp.text)


# --- client-side no Gemini (async + sessão MCP) ---
async def gemini_mcp():
    from mcp import ClientSession
    from mcp.client.stdio import StdioServerParameters, stdio_client

    g = LLM("gemini", "gemini-2.5-flash")
    params = StdioServerParameters(command="npx", args=["-y", "@exemplo/mcp"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            comp = await g.acomplete("Use a ferramenta X", mcp_servers=[session])
            print(comp.text)


# asyncio.run(gemini_mcp())
