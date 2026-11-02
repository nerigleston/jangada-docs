"""Quem chamou: `current_user()` dentro das ferramentas de um servidor MCP por HTTP.

Roda sem rede e sem chave: monta o app com `build_mcp_app` e simula, com o
TestClient do Starlette, a chamada que o gateway do jangada Cloud faria (com os
headers `x-jangada-user-*`). Em produção, quem manda esses headers é o gateway
(modos "Login do jangada" e "OAuth externo").

    pip install "jangada-ai[mcp]" httpx
    python examples/mcp_current_user_example.py
"""
from __future__ import annotations

from jangada_ai import build_mcp_app, current_user

PEDIDOS = {
    "ana@loja.com": [{"numero": "1001", "status": "enviado"}],
    "bia@loja.com": [{"numero": "1002", "status": "em separação"}],
}


def meus_pedidos() -> list[dict]:
    """Lista os pedidos de quem está chamando."""
    usuario = current_user()
    if usuario is None:  # stdio, modo Token ou fora do jangada Cloud
        return []
    return PEDIDOS.get(usuario.email or "", [])


async def quem_sou_eu() -> str:
    """Diz quem está chamando (ferramentas async também enxergam o usuário)."""
    usuario = current_user()
    return f"{usuario.name} <{usuario.email}>" if usuario else "anônimo"


def liberadas():
    """Só a equipe da loja vê todas as ferramentas; o resto vê só `quem_sou_eu`."""
    usuario = current_user()
    return None if usuario and (usuario.email or "").endswith("@loja.com") else ["quem_sou_eu"]


app = build_mcp_app("loja", tools=[meus_pedidos, quem_sou_eu], stateless=True, tool_filter=liberadas)


def chamar(client, metodo: str, params: dict | None = None, **headers: str) -> dict:
    resposta = client.post(
        "/mcp/",
        json={"jsonrpc": "2.0", "id": 1, "method": metodo, "params": params or {}},
        headers={"accept": "application/json, text/event-stream", "mcp-protocol-version": "2025-06-18", **headers},
    )
    return resposta.json()["result"]


if __name__ == "__main__":
    from starlette.testclient import TestClient

    ana = {"x-jangada-user-id": "u1", "x-jangada-user-email": "ana@loja.com", "x-jangada-user-name": "Ana"}
    with TestClient(app) as c:
        print("Ana vê:", [t["name"] for t in chamar(c, "tools/list", **ana)["tools"]])
        print("Visitante vê:", [t["name"] for t in chamar(c, "tools/list", **{"x-jangada-user-id": "v9"})["tools"]])
        r = chamar(c, "tools/call", {"name": "meus_pedidos", "arguments": {}}, **ana)
        print("Pedidos da Ana:", r["content"][0]["text"])
        r = chamar(c, "tools/call", {"name": "quem_sou_eu", "arguments": {}}, **ana)
        print("Quem sou eu:", r["content"][0]["text"])
