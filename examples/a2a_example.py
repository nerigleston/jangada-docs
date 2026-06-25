"""Servidor A2A: expõe agentes da lib via HTTP/JSON-RPC (extra `jangada[a2a]`).

Sobe um app ASGI (Starlette) servindo dois agentes como um servidor A2A:
- descoberta:  GET /.well-known/agent.json  e  GET /agents
- conversa:    POST /            (message/send, JSON)
- streaming:   POST /            (message/stream, SSE)
- por agente:  POST /agents/{nome}

Rode:  uvicorn examples.a2a_example:app --reload
Teste: curl localhost:8000/.well-known/agent.json
       curl -XPOST localhost:8000/ -d '{"jsonrpc":"2.0","id":1,
         "method":"message/send","params":{"message":{"role":"user",
         "parts":[{"kind":"text","text":"qual meu saldo?"}]}}}'
"""
from jangada_ai import LLM, Agent
from jangada_ai.a2a import A2AHandler, build_a2a_app


async def buscar_saldo(conta: str) -> str:
    """Consulta o saldo de uma conta (simulado)."""
    return f"Conta {conta}: R$ 4.250,00"


llm = LLM("openai", "gpt-4o-mini")

sofia = A2AHandler(
    Agent(llm, role="Sofia", goal="assistente financeira", tools=[buscar_saldo]),
    url="http://localhost:8000",
)
orcamento = A2AHandler(
    Agent(llm, role="Orcamento", goal="planejar gastos do mês"),
)

# histórico mantido por contextId entre os turnos (em memória, por padrão).
app = build_a2a_app([sofia, orcamento])
