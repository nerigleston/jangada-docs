# Observabilidade (envio de traces)

`Observability`/`Trace` enviam as chamadas de uma request, agrupadas em um
**lote** (trace), para uma plataforma de observabilidade. Numa request que faz
N chamadas de IA, abre-se 1 trace e registram-se N observations — um único POST
ao final.

```python
import os
from jangada_ai import LLM, Observability

obs = Observability(api_key=os.environ["LOBS_API_KEY"], endpoint="https://sua-api")
llm = LLM("openai", "gpt-4o-mini")

with obs.trace(name="resumo+tradução") as t:
    r1 = llm.complete("Resuma: ...")
    t.log(r1)
    r2 = llm.complete("Traduza: ...")
    t.log(r2)
# flush automático -> 1 POST com as 2 observations
```

## O que é capturado

`t.log(completion)` extrai do `Completion`: `provider`, `model`,
`promptTokens`/`completionTokens` (de `usage`), `costUsd` (de `cost`), o texto
de saída e as **tool calls** que o modelo pediu (`tools`: id/name/args). Você
pode complementar:

```python
t.log(r1, name="extração", input=prompt, latency_ms=820)
t.log(error="timeout ao chamar o modelo")   # registra falha
```

## Detalhes

- `trace(id=...)`: informe um id externo para **acrescentar** observations ao
  mesmo lote em chamadas separadas (idempotente no backend).
- `user_id` / `session_id` / `metadata`: contexto do usuário final do seu app.
- Falhas de rede **não derrubam** sua aplicação (`raise_on_error=False` por
  padrão); o erro vai para o stderr.
- A `api_key` é a chave do projeto, configurada no `.env` do seu projeto.

Os campos de custo/tokens vêm de [Custo e tokens](cost.md).
