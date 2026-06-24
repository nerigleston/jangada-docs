"""Guardrails de escopo: mantém a LLM num domínio e barra falas.

ScopeGuard = blocklist (regex, grátis) + classificador (judge LLM barato).
Ao barrar, devolve um Completion com a mensagem de recusa — no input, nem
chega a gastar o modelo principal.
"""
from jangada_ai import LLM, ScopeGuard

# judge barato/rápido só pra classificar o escopo (separado do modelo principal)
judge = LLM("groq", "llama-3.1-8b-instant")

guard = ScopeGuard(
    scope=(
        "Suporte do sistema e-Gestor: notas fiscais, financeiro, cadastros. "
        "NÃO responde sobre outros assuntos (receitas, política, código, etc.)."
    ),
    judge=judge,
    block=[r"\bsenha\b", "ignore as instruções"],  # barra na hora, sem LLM
    message="Desculpe, só posso ajudar com assuntos do e-Gestor.",
    check="both",  # valida pergunta (input) E resposta (output)
)

llm = LLM("openai", "gpt-4o-mini", guardrails=[guard])

perguntas = [
    "Como emito uma NF-e de venda?",   # dentro do escopo -> responde
    "Me ensina a fazer um bolo?",      # fora do escopo  -> recusa (judge)
    "Qual a senha do admin?",          # blocklist        -> recusa na hora
]

for p in perguntas:
    comp = llm.complete(p)
    barrado = isinstance(comp.raw, dict) and "guardrail" in comp.raw
    print(f"[{'BARRADO' if barrado else 'OK'}] {p}\n  -> {comp.text}\n")
