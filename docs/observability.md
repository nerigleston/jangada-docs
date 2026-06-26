# Observabilidade (envio de traces)

A jangada envia as suas chamadas de LLM para uma plataforma de observabilidade
de dois jeitos: **automático** (zero-config, via `.env`) ou **manual** (agrupando
N chamadas num lote). Em ambos, cada chamada vira uma _observation_ com
provider, modelo, tokens, custo, latência, erro, tool calls e as **capacidades**
de IA usadas.

## Modo automático (zero-config)

Sem instrumentar nada no código: preencha o `.env` do seu projeto e pronto — a
cada `complete`/`parse` (e versões async) a jangada envia **um trace por
chamada**, em background (não bloqueia a sua aplicação).

```bash
# .env
JANGADA_OBSERVABILITY=true
JANGADA_OBSERVABILITY_API_KEY=lobs_xxx        # chave do projeto (dashboard)
# opcional (padrão é a plataforma oficial):
# JANGADA_OBSERVABILITY_ENDPOINT=https://api.jangada.dev.br
```

```python
from jangada_ai import LLM

llm = LLM("openai", "gpt-4o-mini")
resp = llm.complete("Resuma: ...")   # já enviado à plataforma, sozinho
```

A flag precisa ser "truthy" (`1`/`true`/`yes`/`on`/`sim`) **e** o token presente;
faltando qualquer um, o modo fica desligado e nada é enviado (custo zero). Falhas
de rede nunca derrubam a aplicação — o envio é best-effort numa thread daemon.

> O modo automático manda **uma chamada por trace** (sem agrupar). Para juntar
> várias chamadas de uma request num único lote, use o modo manual abaixo.

## Modo manual (lotes)

`Observability`/`Trace` agrupam as chamadas de uma request num **lote** (trace)
e enviam tudo num único POST ao final do `with`:

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

# tool calls + o resultado que VOCÊ executou (casa por id, senão por name):
t.log(comp, tool_results={"get_weather": "25°C", "somar": 3})
```

## Capacidades (capabilities)

Cada observation registra **quais capacidades de IA** foram usadas — `tools`,
`mcp`, `a2a`, `vision`, `audio`, `documents`, `rag`, `structured_output`,
`guardrails`, `cache`, `agents`, `embeddings`. No dashboard viram **badges**,
**filtro** e a quebra **Analytics → Uso por capacidade**.

No **modo automático**, a jangada detecta sozinha a partir dos argumentos da
chamada: `images=` → `vision`, `files=` → `documents`, `tools=` → `tools`,
`mcp_servers=` → `mcp`, `parse()` → `structured_output`, `guardrails` →
`guardrails`. `tools` também é derivado quando o modelo pede tool calls.

No **modo manual**, marque o que quiser no `t.log(...)` (normalizado e sem
duplicatas; valores fora da lista também são aceitos):

```python
t.log(r, capabilities=["rag", "structured_output"])
```

## No dashboard

Em [app.jangada.dev.br](https://app.jangada.dev.br) você acompanha tudo:

- **Traces e detalhe** — cada lote e suas observations (provider, modelo, tokens,
  custo, latência, tool calls e capacidades), em tabela ou waterfall.
- **Analytics** — custo, chamadas, tokens, taxa de erro e latência (p50/p95/p99),
  com quebra por modelo, provider e capacidade e série temporal por dia.
- **Filtros e exportação** — filtre por modelo, provider, erros, datas,
  userId/sessionId, custo mínimo e capacidade; exporte em CSV/JSON.
- **Live tail** — traces em tempo real, com pausar/retomar.
- **Anomalias** — avisos automáticos quando custo/latência/erro fogem do
  baseline de 7 dias.
- **Alertas** — regras de custo diário ou taxa de erro.
- **Scores** — avaliações por trace (feedback humano ou LLM-as-judge).
- **Orçamento** — teto de custo mensal por projeto, com acompanhamento e projeção.

## Detalhes

- `trace(id=...)`: informe um id externo para **acrescentar** observations ao
  mesmo lote em chamadas separadas (idempotente no backend).
- `user_id` / `session_id` / `metadata`: contexto do usuário final do seu app.
- Falhas de rede **não derrubam** sua aplicação (`raise_on_error=False` por
  padrão); o erro vai para o stderr.
- A `api_key` é a chave do projeto, configurada no `.env` do seu projeto.

Os campos de custo/tokens vêm de [Custo e tokens](cost.md).
