# Custo e tokens

Toda resposta bem-sucedida volta com `usage` (tokens) e `cost` (USD estimado).

```python
comp = llm.complete("...")
print(comp.usage)   # {"input_tokens": ..., "output_tokens": ...}
print(comp.cost)    # ex.: 0.000123  (USD, aproximado)
```

O cliente chama `pricing.compute_cost()` após cada sucesso e seta
`Completion.cost`. `FlowResult` e `GraphResult` **agregam** `usage`/`cost` ao
longo da cadeia.

## Tabela de preços

Os preços ficam em `pricing.py` (aproximados, por 1M de tokens). Você pode
registrar/ajustar:

```python
from jangada_ai import register_price, price_for

register_price("meu-modelo", input=0.5, output=1.5)   # USD por 1M tokens
print(price_for("gpt-4o-mini"))
```

> ⚠️ Os valores são **aproximados** e servem para estimativa/observabilidade —
> não trate como fonte de billing.

## Onde isso aparece

- `Completion.cost` / `Completion.usage` em cada chamada.
- Totais agregados em [Fluxos e Graph](flows.md).
- No [Debug passo a passo](debug.md), o custo de cada etapa é exibido no trace.
