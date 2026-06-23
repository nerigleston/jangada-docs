# MCP (Model Context Protocol)

Conecte servidores MCP às chamadas via `mcp_servers=[...]`. **Todos os providers
suportam MCP**, mas de formas diferentes — e a jangada usa o jeito nativo de cada
SDK.

## Dois modelos (importante)

- **Remoto (URL)** — `MCPServer(url=...)`: o **provider** conecta no servidor MCP
  e executa as tools (server-side). Você não roda nada. → **Anthropic, OpenAI, Groq**.
- **Client-side (sessão)** — você passa uma `ClientSession` do pacote `mcp`: o
  **SDK** chama as tools localmente (automatic function calling). → **Gemini**.

| Provider | Modelo | Como | Observação |
|----------|--------|------|------------|
| Anthropic | remoto (URL) | Messages API (`mcp_servers` + `MCPToolset`, header beta) | **beta** (`mcp-client-2025-11-20`) |
| OpenAI | remoto (URL) | **Responses API** (`tools=[{type:"mcp"}]`) | usa a Responses API, não `chat.completions` |
| Groq | remoto (URL) | Responses API (compatível com a OpenAI) | beta — a jangada usa o **client OpenAI no `base_url` do Groq** por baixo (precisa do pacote `openai` instalado) |
| Gemini | client-side (sessão) | `tools=[session]` (automatic function calling) | **só no async** (`acomplete`) — a sessão é assíncrona |

## Remoto (Anthropic / OpenAI / Groq)

```python
from jangada_ai import LLM, MCPServer

llm = LLM("anthropic", "claude-opus-4-8")   # ou ("openai", "gpt-4o"), ("groq", ...)
comp = llm.complete(
    "Liste as issues abertas do repositório.",
    mcp_servers=[MCPServer(
        url="https://mcp.exemplo.com/sse",
        name="github",
        authorization_token="TOKEN",     # opcional (OAuth/Bearer)
        allowed_tools=["list_issues"],   # opcional (restringe as tools)
    )],
)
print(comp.text)   # o provider já executou as tools do MCP
```

## Client-side (Gemini, async)

A sessão MCP é assíncrona, então use **`acomplete`**:

```python
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from jangada_ai import LLM

llm = LLM("gemini", "gemini-2.5-flash")
params = StdioServerParameters(command="npx", args=["-y", "@exemplo/mcp"])

async with stdio_client(params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        comp = await llm.acomplete("Use a ferramenta X", mcp_servers=[session])
        print(comp.text)
```

> No Gemini, `complete()` (sync) com sessão levanta `UnsupportedError` pedindo
> `acomplete()`. Passar uma `MCPServer(url=...)` no Gemini também levanta — ele é
> client-side. E passar uma sessão no Anthropic/OpenAI/Groq levanta — eles são
> remotos por URL.

## Alternativa portável (loop manual com `tools=`)

Se você já gerencia um cliente MCP (ex.: FastMCP) e quer controle total em
**qualquer provider** (inclusive sync), liste as tools do MCP e use o
[tool calling](tools.md) normal: passe-as em `tools=[...]`, receba
`comp.tool_calls`, execute via seu cliente MCP e reenvie com
`Message.tool_results(...)`. Isso não depende do MCP nativo de cada SDK.

## Exemplo

[`examples/mcp_example.py`](https://raw.githubusercontent.com/nerigleston/jangada-docs/main/examples/mcp_example.py) — script executável.
