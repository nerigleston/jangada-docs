# Streaming

Receba tokens incrementais com `stream()` (sync) ou `astream()` (async).

```python
for token in llm.stream("Conte sobre {{x}}", x="João Pessoa"):
    print(token, end="")
```

```python
async for token in llm.astream("..."):   # ex.: FastAPI StreamingResponse
    ...
```

## Retry e fallback no streaming

O retry e o fallback acontecem **antes do primeiro token**: se a abertura do
stream falhar com erro transitório, a jangada tenta de novo (backoff) e, se
preciso, cai para o próximo candidato — tudo antes de você receber qualquer
conteúdo. Depois que o primeiro token sai, o stream segue até o fim.

Veja [Retry e fallback](retry-fallback.md) para a política completa.

## Observações

- `stream()`/`astream()` aceitam os mesmos `system=`, `history=`, `images=`,
  `files=` e `params=` das outras chamadas.
- Para custo e tokens use as chamadas não-stream (`complete`/`parse`), que
  retornam `usage`/`cost` na resposta — veja [Custo e tokens](cost.md).
