# Debug passo a passo

Ative `debug=True` para um trace de cada chamada: provider/modelo, params,
retries, fallback, tokens, custo e duração — por agente.

```python
from jangada import LLM

llm = LLM("openai", "gpt-4o-mini", debug=True, name="extrator")
llm.complete("...")
```

O `Debugger` registra os eventos da cadeia:

- `start` — provider, modelo e params da tentativa
- `retry` — erro, número da tentativa e atraso do backoff
- `fallback` — para qual provider/modelo caiu
- `end` — `Completion` resultante e duração em ms
- `error` — erro normalizado quando o candidato esgota as tentativas

O parâmetro `name=` rotula o agente no trace, útil quando há vários `LLM`
diferentes numa mesma orquestração ([Flow/Graph](flows.md)).

Relacionado: [Retry e fallback](retry-fallback.md), [Custo e tokens](cost.md),
[Erros](errors.md).
