# Observabilidade (automática)

A jangada envia as suas chamadas de LLM para a plataforma de observabilidade de
forma **automática** (zero-config): basta configurar o `.env`. Cada chamada vira
uma _observation_ com provider, modelo, tokens, custo, latência, tool calls e as
**capacidades** de IA usadas — enviada em background, sem instrumentar o código.

## Ativar (zero-config)

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

Embeddings também são instrumentados automaticamente. Isso inclui os embeddings
gerados por RAG, cache semântico e indexação em lote:

```python
embedder = LLM("openai", "text-embedding-3-small")

with observability_session(name="rag.documents.ingest"):
    vectors = embedder.embed(["primeiro chunk", "segundo chunk"])
```

A observation registra latência, tokens de entrada, custo estimado, a capability
`embeddings` e o array completo de vetores em `output`. O output observado mantém
sempre o formato de lote (`[[...], [...]]`), inclusive quando `embed()` recebe uma
única string. O retorno público não muda: continua sendo um vetor para `str` ou uma
lista de vetores para uma lista de textos.

No Gemini, a contagem segue esta ordem: `usage_metadata` da própria resposta;
`count_tokens()` com o mesmo modelo e lote quando o usage estiver ausente; e,
somente se ambos falharem, estimativa local de aproximadamente 4 caracteres por
token. O preço nunca fica no adapter: `compute_cost()` resolve o modelo pelo
catálogo atualizado de `jangada.dev.br/prices.json`. As observations indicam a
origem em `usageSource` (`provider`, `count_tokens` ou `estimated`) e marcam
`usageEstimated=true` apenas no último fallback.

A flag precisa ser "truthy" (`1`/`true`/`yes`/`on`/`sim`) **e** o token presente;
faltando qualquer um, o modo fica desligado e nada é enviado (custo zero). Falhas
de rede nunca derrubam a aplicação — o envio é best-effort numa thread daemon.

## Agrupar por lote

Por padrão cada chamada vira um trace próprio. Para agrupar várias chamadas de
uma request no **mesmo lote** (mesmo sendo enviadas uma a uma), abra um escopo
com `observability_session`: um id de lote é gerado e todas as chamadas de dentro
o compartilham — o backend as agrupa no mesmo trace.

```python
from jangada_ai import LLM, observability_session

llm = LLM("openai", "gpt-4o-mini")

with observability_session(name="resumo+tradução", user_id="cliente-123"):
    r1 = llm.complete("Resuma: ...")     # observation no mesmo trace
    r2 = llm.complete("Traduza: ...")    # idem — agrupadas pelo id do lote
```

`observability_session` aceita `id` (reaproveita um id externo), `name`,
`user_id`, `session_id` e `metadata`, e devolve o id do lote. Funciona em código
sync e async (usa `contextvars`).

## Feedback de produção

Capture a reação do usuário final (👍/👎 ou um score) e anexe ao trace com
`feedback()`. Use o **id do lote** devolvido por `observability_session`. É
**best-effort** (nunca derruba a app): devolve `True` se enviou, `False` se faltou
chave ou deu erro de rede.

```python
from jangada_ai import LLM, observability_session, feedback

llm = LLM("openai", "gpt-4o-mini")

with observability_session(name="suporte") as trace_id:
    resp = llm.complete("Como emito uma NF?")

# mais tarde, quando o usuário avaliar a resposta:
feedback(trace_id, 1, comment="resolveu meu problema")   # 👍
# feedback(trace_id, -1, comment="resposta errada")      # 👎
```

O feedback vira um `Score` no trace (origem `api`), aparece no dashboard junto dos
👍/👎 humanos e fecha o loop: um 👎 pode ser **promovido a exemplo** de dataset
(pelo dashboard) e virar caso de regressão nas [evals](eval.md).

## O que é capturado

De cada chamada: `provider`, `model`, `promptTokens`/`completionTokens` (de
`usage`), `costUsd` (de `cost`), latência, o **input** (mensagens ou textos de
embedding; conteúdos muito longos são truncados), o **output** (texto da resposta,
ou quantidade/dimensão dos embeddings) e as **tool calls** que o modelo pediu
(`tools`: id/name/args).

Cada observation tem um **status**: `OK`, ou **`INCOMPLETE`** quando a resposta
foi cortada por limite de tokens (`finish_reason == "length"`). O motivo de parada
normalizado também é enviado em **`finishReason`**. No dashboard isso vira um badge
(âmbar para incompleto) e entra no filtro de status.

## Capacidades (capabilities)

Cada observation registra **quais capacidades de IA** foram usadas — `tools`,
`mcp`, `a2a`, `vision`, `audio`, `documents`, `rag`, `structured_output`,
`guardrails`, `cache`, `agents`, `embeddings`. No dashboard viram **badges**,
**filtro** e a quebra **Analytics → Uso por capacidade**.

A detecção é automática a partir dos argumentos da chamada: `images=` → `vision`,
`files=` → `documents`, `tools=` → `tools`, `mcp_servers=` → `mcp`, `parse()` →
`structured_output`, `guardrails` → `guardrails`. `tools` também é derivado
quando o modelo pede tool calls.

`embed()`/`aembed()` registram `embeddings` diretamente. Assim, um
`observability_session` que só contenha ingestão RAG deixa de ser um escopo vazio
e aparece normalmente no dashboard.

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

- A `api_key` é a chave do projeto, gerada no dashboard e configurada no `.env`.
- Reusar o mesmo id de lote (via `observability_session(id=...)`) **acrescenta**
  observations ao mesmo trace de forma idempotente no backend.
- Os campos de custo/tokens vêm de [Custo e tokens](cost.md).
