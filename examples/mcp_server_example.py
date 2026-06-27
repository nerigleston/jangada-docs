"""Servidor MCP nativo do jangada (stdio) — exemplo runnable.

Expõe duas ferramentas para qualquer cliente MCP (Claude Desktop, Cursor, ou o
MCPClient do jangada). Rode:  python examples/mcp_server_example.py

No Claude Desktop / Cursor, aponte um servidor MCP do tipo stdio para este arquivo.
Para HTTP: troque por serve_mcp(..., transport="streamable-http", port=8000).
"""
from jangada_ai import serve_mcp


def somar(a: float, b: float) -> float:
    """Soma dois números e devolve o resultado."""
    return a + b


def saudacao(nome: str) -> str:
    """Devolve uma saudação para a pessoa."""
    return f"Olá, {nome}! Bem-vindo(a)."


if __name__ == "__main__":
    serve_mcp("jangada-demo", tools=[somar, saudacao])  # stdio
