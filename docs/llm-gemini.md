# Gemini

Provider `gemini`. Adapter sobre o SDK `google-genai`. Tem um único `Client`; o
async fica em `client.aio`.

```bash
pip install "jangada-ai[gemini]"
```

- **`provider=`**: `"gemini"`
- **Variável de ambiente**: `GEMINI_API_KEY` (ou `GOOGLE_API_KEY`)

```python
from jangada import LLM
llm = LLM("gemini", "gemini-2.5-flash")
```

## O que faz

- **Texto** e **streaming** (`generate_content` / `generate_content_stream`).
- **Structured output** (`parse`): `config.response_schema=Modelo` +
  `response_mime_type="application/json"` → `resp.parsed`.
- **Vision** (`images=`): imagens viram `types.Part.from_bytes`.
- **Documentos** (`files=`): extração de texto local.
- **Detecção de objetos** (`detect_objects`): **o mais preciso** — o formato de
  bounding box 0–1000 é nativo do treino do Gemini.
- **Transcrição de áudio** (`transcribe`): multimodal — o áudio entra como
  `Part.from_bytes` junto de uma instrução; **não** é endpoint dedicado.

## Estrutura e quirks

- **Mensagens**: o papel `system` vira `system_instruction` no
  `GenerateContentConfig` (não é uma mensagem comum); `assistant` vira `model`.
- **Parâmetros canônicos → config**: `max_tokens`→`max_output_tokens`,
  `stop`→`stop_sequences`; `temperature`/`top_p`/`top_k`/`seed` passam direto.
  É o único provider com `top_k`.
- **Perfil de modelo** (`profiles.py`): `gemini-3.x` descarta sampling
  (`temperature`/`top_p`/`top_k`) e usa `thinking_level` no lugar de
  `thinking_budget`. Function calling multi-turn no 3.x exige preservar as
  *thought signatures* (integridade do histórico). Veja
  [Parâmetros e perfis](parameters.md).
- **Resposta** (`Completion`): `usage` vem de `usage_metadata`
  (`prompt_token_count`/`candidates_token_count`).

## Por que é o "canivete suíço" aqui

É o único que cobre vision, detecção e áudio **sem endpoints separados** —
tudo via `generateContent`. Veja [Matriz de capacidades](capabilities.md).
