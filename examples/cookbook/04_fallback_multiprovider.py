"""Fallback multi-provider: o mesmo código, resiliente a falhas de API.

Caso real: produção não pode cair porque um provider deu rate limit ou 5xx. A
jangada tenta o primário (com retries) e, se ele falhar de forma "failover-able"
(rate limit, timeout, 5xx, 404), cai pro reserva — sem você tratar nada à mão.
Cada resposta volta com `usage` e `cost` estimado.

Rode (precisa de pelo menos 2 providers configurados):
    pip install "jangada-ai[openai,anthropic]"
    export OPENAI_API_KEY=sk-...  ANTHROPIC_API_KEY=sk-ant-...
    python examples/cookbook/04_fallback_multiprovider.py
"""
from __future__ import annotations

from jangada_ai import LLM

# primário e reserva — interface idêntica, só muda provider/modelo
primario = LLM("openai", "gpt-4o-mini")
reserva = LLM("anthropic", "claude-haiku-4-5-20251001")

llm = primario.with_fallback(reserva)


def main() -> None:
    comp = llm.complete("Explique {{tema}} em uma frase.", tema="tolerância a falhas")
    print("Resposta:", comp.text)
    print(f"Provider usado: {comp.provider} / {comp.model}")
    print(f"Tokens: {comp.usage}")
    print(f"Custo estimado: US$ {comp.cost:.6f}" if comp.cost else "Custo: (modelo sem preço)")


if __name__ == "__main__":
    main()
