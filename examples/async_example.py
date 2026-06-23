"""Async: acomplete, aparse e astream — ideal para FastAPI."""
import asyncio

from pydantic import BaseModel

from jangada_ai import LLM


class Resumo(BaseModel):
    titulo: str
    pontos: list[str]


async def main() -> None:
    llm = LLM("anthropic", "claude-opus-4-8")

    # texto
    resp = await llm.acomplete("Explique {{tema}} em 1 frase.", tema="MCP")
    print(resp.text)

    # structured
    out = await llm.aparse("Resuma em 3 pontos:\n{{texto}}", Resumo, texto="...")
    print(out.parsed.titulo, out.parsed.pontos)

    # streaming
    async for token in llm.astream("Conte uma história curta sobre {{x}}", x="João Pessoa"):
        print(token, end="", flush=True)
    print()


if __name__ == "__main__":
    asyncio.run(main())
