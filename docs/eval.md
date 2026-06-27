# Avaliação (evals): Datasets, Evaluators e Experiments

A lib promete **trocar provider/modelo sem mudar o código**. As _evals_ são a
outra metade: **provar que a troca não piorou a qualidade nem estourou o custo**.
Você roda um `target` sobre um conjunto de casos (`Dataset`), dá notas com
`Evaluator`s (heurística e/ou LLM juiz) e compara execuções (`Experiment`) por
**acerto × R$ × latência**.

Funciona **100% offline** (igual à observabilidade): `evaluate()` devolve os
scores localmente; enviar ao painel é opcional (`push=True`).

```python
from jangada_ai import LLM
from jangada_ai.eval import Evaluator, Dataset, evaluate
```

## As peças

| Peça | Responde |
|------|----------|
| `Dataset`/`Example` | "Em cima de quais casos eu meço?" (entradas + gabarito) |
| `Evaluator` | "Essa saída está boa?" (heurística ou juiz LLM) |
| `evaluate()` | roda o `target` sobre o dataset, aplica os evaluators e agrega |
| `ExperimentResult` | o resultado: notas por evaluator, custo, p50, erros |

## 1. Dataset — os casos

Um `Example` tem `inputs` (o que vai para o `target`), `reference` (gabarito,
opcional) e `metadata`. Um `Dataset` é uma coleção iterável de exemplos.

```python
# da memória
ds = Dataset.from_records([
    {"inputs": {"q": "Capital da França?"}, "reference": "Paris"},
    {"inputs": {"q": "2 + 2?"},            "reference": "4"},
], name="perguntas")

# de um arquivo JSONL (uma linha por exemplo: {"inputs": {...}, "reference": ...})
ds = Dataset.from_jsonl("casos.jsonl", name="casos")
```

## 2. Evaluators — as notas

Dois construtores. Ambos devolvem um `Evaluator` com uma `key` (o nome do score).

### Heurística (`Evaluator.fn`)

Função pura `(output, reference)` que devolve **float**, **bool** ou um
`EvalResult`. Sem rede — é só código seu.

```python
exato = Evaluator.fn(
    "exato",
    lambda out, ref: out.text.strip().lower() == ref.lower(),  # bool → 1.0/0.0
)

# com EvalResult para anexar um comentário
from jangada_ai.eval import EvalResult
tamanho = Evaluator.fn(
    "curto",
    lambda out, ref: EvalResult(1.0 if len(out.text) < 200 else 0.0, comment="len ok"),
)
```

> `out` é o que o seu `target` devolveu — tipicamente um `Completion` (com
> `.text`, `.parsed`, `.cost`). `ref` é o `reference` do exemplo.

### Juiz LLM (`Evaluator.judge`)

Um LLM avalia a saída. Por baixo é um `parse()` com schema fixo
`{score, reason}` (a mesma mecânica do `ScopeGuard`). Use para critérios
subjetivos (utilidade, tom, equivalência semântica).

```python
util = Evaluator.judge(
    "util",
    "A resposta responde à pergunta de forma correta e útil? score de 0 a 1.",
    judge=LLM("openai", "gpt-4o-mini"),
)
```

O juiz pode ser **qualquer** provider/modelo — inclusive um diferente do que está
sendo avaliado (o padrão recomendado: um modelo barato julgando outro).

## 3. evaluate() — rodar e agregar

`evaluate(data, target, evaluators)` itera os exemplos, chama
`target(example) -> output`, aplica cada evaluator ao par `(output, reference)`
e agrega o resultado.

```python
def alvo(ex):
    llm = LLM("openai", "gpt-4o-mini")
    return llm.complete(ex.inputs["q"])

res = evaluate(ds, target=alvo, evaluators=[exato, util], name="baseline")

print(res.summary())
# {'exato': 0.9, 'util': 0.95, 'costUsd': 0.0021, 'p50_ms': 740, 'count': 2, 'errors': 0}
```

O `summary()` (= `res.aggregate`) traz:

- uma **média por evaluator** (pela `key`),
- `costUsd` — custo somado do `target` (vem de `Completion.cost`),
- `evalCostUsd` — custo somado dos **juízes** (quando há `Evaluator.judge`),
- `p50_ms` — latência mediana,
- `count` e `errors`.

Cada item fica em `res.runs` (lista de dicts com `inputs`, `output`, `scores`,
`costUsd`, `latencyMs`, `error`). Um `target` que levanta exceção **não derruba**
o experimento: vira um run com `error` preenchido.

### Async e concorrência

`aevaluate(...)` é a versão assíncrona; `target` pode ser sync ou coroutine.
`max_concurrency` limita exemplos rodando em paralelo.

```python
res = await aevaluate(ds, target=alvo_async, evaluators=[exato], max_concurrency=8)
```

## 4. Comparar modelos (o caso que importa)

O valor real: rodar **o mesmo dataset** com modelos diferentes e decidir com
evidência. Só muda o modelo no `target`.

```python
def alvo(modelo):
    def run(ex):
        return LLM("openai", modelo).complete(ex.inputs["q"])
    return run

gpt   = evaluate(ds, target=alvo("gpt-5"),          evaluators=[exato, util], name="gpt5")
flash = evaluate(ds, target=alvo("gemini-3-flash"), evaluators=[exato, util], name="flash")

print(gpt.summary())    # {'exato': 0.94, 'util': 0.97, 'costUsd': 0.21, ...}
print(flash.summary())  # {'exato': 0.90, 'util': 0.95, 'costUsd': 0.02, ...}
# 4 pontos a menos, ~10× mais barato → migra com prova, não no escuro.
```

## 5. Enviar ao painel (`push=True`)

Com a observabilidade configurada (mesma chave de projeto), `push=True` envia o
experiment (com runs e scores) para o backend — e ele aparece no dashboard, nas
abas **Experiments** (tabela comparativa) e **Datasets** (com gráfico de score ao
longo do tempo).

```bash
# .env (mesma config da observabilidade)
JANGADA_OBSERVABILITY_API_KEY=lobs_xxx
# JANGADA_OBSERVABILITY_ENDPOINT=https://api.jangada.dev.br  # opcional
```

```python
res = evaluate(
    ds, target=alvo("gpt-5"), evaluators=[exato, util],
    name="gpt5",
    push=True,
    target_info={"provider": "openai", "model": "gpt-5"},  # descritivo, aparece no painel
)
print(res.pushed, res.push_error)  # True None  (best-effort: nunca derruba)
```

O `push` é **best-effort**: falha de rede ou ausência de chave não levanta — só
marca `res.pushed = False` e `res.push_error`. Cada run guarda o `traceId` quando
disponível, ligando o score de volta ao trace que o gerou.

## Como funciona (resumo)

- `Evaluator.fn` roda local (sem rede). `Evaluator.judge` faz um `parse()` no LLM
  juiz com schema `{score, reason}` e extrai a nota.
- `evaluate()` mede latência por exemplo, lê `Completion.cost` para o custo do
  target, soma o custo dos juízes em `evalCostUsd`, e calcula média/p50/erros.
- Nada vaza tipo de SDK: o `target` devolve o que quiser; os evaluators recebem
  esse objeto direto (duck-typing sobre `Completion`).
- `push` reusa a config da observabilidade e fala com `POST /v1/experiments`.

## Ver também

- [Observabilidade](observability.md) — traces automáticos por chamada.
- [Custo e tokens](cost.md) — de onde vem `Completion.cost`.
- [Structured output](structured-output.md) — base do `Evaluator.judge`.
