"""Evals: medir qualidade e comparar modelos com prova (score × custo × latência).

- Dataset: casos com gabarito.
- Evaluators: heurística (Evaluator.fn) + juiz LLM (Evaluator.judge).
- evaluate(): roda um target sobre o dataset e agrega.
- Comparação: mesmo dataset, modelos diferentes → decide com evidência.

Roda offline (devolve os scores). Para enviar ao painel, use push=True com
JANGADA_OBSERVABILITY_API_KEY no .env (ver docs/observability.md).
"""
from jangada_ai import LLM
from jangada_ai.eval import Dataset, Evaluator, evaluate

# 1) Dataset com gabarito
ds = Dataset.from_records(
    [
        {"inputs": {"q": "Qual a capital da França?"}, "reference": "Paris"},
        {"inputs": {"q": "Quanto é 7 x 6?"}, "reference": "42"},
        {"inputs": {"q": "Cite um planeta do sistema solar."}, "reference": "Marte"},
    ],
    name="perguntas-basicas",
)

# 2) Evaluators: heurística (contém a referência) + juiz LLM (utilidade)
contem = Evaluator.fn(
    "contem_ref",
    lambda out, ref: ref.lower() in out.text.lower(),
)
util = Evaluator.judge(
    "util",
    "A resposta responde corretamente à pergunta? Dê score de 0 a 1.",
    judge=LLM("openai", "gpt-4o-mini"),  # juiz barato, separado do alvo
)


def alvo(modelo: str):
    """Cria um target que responde com o `modelo` informado."""

    def run(ex):
        return LLM("openai", modelo).complete(ex.inputs["q"])

    return run


if __name__ == "__main__":
    # 3) Roda um experiment por modelo, sobre o MESMO dataset
    for modelo in ("gpt-4o-mini", "gpt-5"):
        res = evaluate(
            ds,
            target=alvo(modelo),
            evaluators=[contem, util],
            name=modelo,
            # push=True, target_info={"provider": "openai", "model": modelo},
        )
        print(f"\n=== {modelo} ===")
        print(res.summary())
        for r in res.runs:
            print("  -", r["inputs"]["q"], "→", r["scores"], r.get("error") or "")
