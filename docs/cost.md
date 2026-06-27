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
