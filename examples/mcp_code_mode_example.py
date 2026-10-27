"""Servidor MCP do jangada em **Code Mode** (stdio) — exemplo runnable.

Em vez de expor cada ferramenta, o servidor expõe só `search`, `get_schema` e
`execute`: o cliente (Claude, Cursor...) acha as tools que precisa e escreve um
trecho de Python que as chama via `await call_tool(nome, params)` num sandbox.
Bom para catálogos grandes e para encadear várias chamadas numa ida só.

Requer:  pip install "jangada-ai[code-mode]"
Rode:    python examples/mcp_code_mode_example.py
"""
from jangada_ai import CodeMode, serve_mcp


def buscar_cliente(cliente_id: int) -> dict:
    """Busca os dados de um cliente pelo id."""
    return {"id": cliente_id, "nome": f"Cliente {cliente_id}", "vip": cliente_id % 2 == 0}


def listar_pedidos(cliente_id: int, status: str = "aberto") -> list:
    """Lista os pedidos de um cliente, filtrando pelo status."""
    return [{"pedido": i, "cliente": cliente_id, "valor": 10.0 * i, "status": status} for i in range(1, 4)]


def cancelar_pedido(pedido: int, motivo: str) -> str:
    """Cancela um pedido informando o motivo."""
    return f"pedido {pedido} cancelado ({motivo})"


if __name__ == "__main__":
    # O modelo pode, num único `execute`:
    #   c = await call_tool("buscar_cliente", {"cliente_id": 7})
    #   peds = await call_tool("listar_pedidos", {"cliente_id": 7})
    #   return {"cliente": c["nome"], "total": sum(p["valor"] for p in peds)}
    serve_mcp(
        "loja",
        tools=[buscar_cliente, listar_pedidos, cancelar_pedido],
        code_mode=CodeMode(limits={"max_feed_duration_secs": 10}),
    )
