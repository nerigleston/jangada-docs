"""Agent: tools async, conversa multi-turno (history), streaming e Agent Card.

Mostra os recursos do `Agent` num só lugar:
- tool **assíncrona** (`async def`) executada no `arun`;
- continuidade de diálogo via `history=` (você persiste/reinjeta os turnos);
- `astream` para emitir a resposta final token-a-token;
- `card()` com os metadados descobríveis (vocabulário A2A).

Rode com uma chave real (ex.: OPENAI_API_KEY) — ajuste provider/model à vontade.
"""
import asyncio

from jangada_ai import LLM, Agent
from jangada_ai.message import Message


async def buscar_saldo(conta: str) -> str:
    """Consulta o saldo de uma conta (simula um acesso async a banco/API)."""
    await asyncio.sleep(0)  # aqui entraria o I/O real (psycopg async, httpx, ...)
    return f"Conta {conta}: saldo de R$ 4.250,00"


async def main() -> None:
    llm = LLM("openai", "gpt-4o-mini")
    sofia = Agent(
        llm,
        role="Sofia",
        goal="ser uma assistente financeira objetiva",
        tools=[buscar_saldo],
    )

    # 1) arun com tool async
    res = await sofia.arun("Qual o saldo da conta corrente?")
    print("Resposta:", res.text)
    print("Custo/uso:", res.cost, res.usage)

    # 2) continuidade multi-turno: reinjete os turnos anteriores
    historico = [
        Message("user", "Qual o saldo da conta corrente?"),
        Message("assistant", res.text),
    ]
    res2 = await sofia.arun("E isso dá pra cobrir uma fatura de R$ 5.000?",
                            history=historico)
    print("\nTurno 2:", res2.text)

    # 3) streaming da resposta final
    print("\nStreaming: ", end="")
    async for token in sofia.astream("Resuma minha situação em uma frase."):
        print(token, end="", flush=True)
    print()

    # 4) Agent Card (descoberta / A2A)
    print("\nCard:", sofia.card(url="https://app.exemplo/agents/sofia"))


if __name__ == "__main__":
    asyncio.run(main())
