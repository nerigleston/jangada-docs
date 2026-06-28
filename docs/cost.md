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

register_price("meu-modelo", 0.5, 1.5)   # USD por 1M tokens (input, output)
print(price_for("gpt-4o-mini"))
```

> ⚠️ Os valores são **aproximados** e servem para estimativa/observabilidade —
> não trate como fonte de billing.

## Preços sempre atualizados (sem atualizar a lib)

A tabela embutida no `pricing.py` é só o **fallback offline**. Como preços de API
mudam toda hora, a jangada publica um catálogo (`prices.json`) e o aplica **sozinha,
sem você escrever nada** — e **sem precisar dar `pip install -U`**.

**Automático (padrão).** Na primeira vez que um custo é calculado (logo abaixo de
cada chamada de provider, em `compute_cost`), a lib dispara **em background** um
refresh do catálogo, cacheado por **1 dia**. Você só usa o LLM normalmente:

```python
llm = jangada_ai.LLM(provider="openai", model="gpt-4o-mini")
comp = llm.complete("...")
print(comp.cost)   # já tende a usar os preços do dia (refresh roda em background)
```

- **Não bloqueia**: a busca roda numa thread daemon; o `import` nunca toca a rede e
  a chamada não trava. As primeiras chamadas usam o embutido até o refresh terminar.
- **No máximo 1x/dia**: cache em `~/.cache/jangada/prices.json` (e 1x por processo).
- **Resiliente**: rede falhou? fica no cache/embutido — nunca levanta.
- **Desligar**: env `JANGADA_NO_PRICE_REFRESH=1`.

**Manual (`refresh_prices`).** Para controle explícito/síncrono — garantir preços
frescos no boot, forçar agora, ou apontar outra URL:

```python
jangada_ai.refresh_prices()                          # síncrono, respeita o cache
jangada_ai.refresh_prices(ttl=3600, force=True)      # revalida/ força agora
jangada_ai.refresh_prices(url="https://meu-espelho/prices.json")
```

Default da URL: `https://jangada.dev.br/prices.json` (override por `url=` ou env
`JANGADA_PRICES_URL`; não precisa de `.env`).

O override manual (`register_price`) tem prioridade sobre tudo — use para fixar um
número exato de um modelo específico.

## Custo multimodal

- **Imagem (vision)**: não há preço separado — os providers já contam os tokens da
  imagem dentro de `input_tokens`. O custo da imagem já sai pela tabela normal.
- **Áudio (transcrição)**: cobrado **por minuto**, não por token. O custo só sai
  quando o `usage` traz a duração (`audio_seconds`): passe
  `response_format="verbose_json"` na transcrição **ou** informe a duração em
  `Audio.from_bytes(dados, mime, duration=...)`. Registre/ajuste com
  `register_audio_price("whisper-1", 0.006)` (USD por minuto).
- **Detecção**: `detect_objects`/`adetect_objects` devolvem só `list[Detection]`
  (sem custo). Para o custo, use `detect_objects_full`/`adetect_objects_full`, que
  devolvem um `DetectionResult` com `.detections` **e** `.completion`/`.cost`/`.usage`.

## Onde isso aparece

- `Completion.cost` / `Completion.usage` em cada chamada.
- Totais agregados em [Fluxos e Graph](flows.md).
- No [Debug passo a passo](debug.md), o custo de cada etapa é exibido no trace.

## Exemplo

[`examples/retry_cost_example.py`](https://raw.githubusercontent.com/nerigleston/jangada-docs/main/examples/retry_cost_example.py) — script executável.

[`examples/pricing_refresh_example.py`](https://raw.githubusercontent.com/nerigleston/jangada-docs/main/examples/pricing_refresh_example.py) — preços dinâmicos com `refresh_prices()`.
