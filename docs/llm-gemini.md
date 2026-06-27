# Gemini

Provider `gemini`. Adapter sobre o SDK `google-genai`. Tem um único `Client`; o
async fica em `client.aio`.

```bash
pip install "jangada-ai[gemini]"
```

- **`provider=`**: `"gemini"`
- **Variável de ambiente**: `GEMINI_API_KEY` (ou `GOOGLE_API_KEY`)

```python
from jangada_ai import LLM
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
  (`temperature`/`top_p`/`top_k`). Function calling multi-turn no 3.x exige
  preservar as *thought signatures* (integridade do histórico). Veja
  [Parâmetros e perfis](parameters.md).
- **Resposta** (`Completion`): `usage` vem de `usage_metadata`
  (`prompt_token_count`/`candidates_token_count`).

## Thinking (raciocínio) — você passa só `thinking_budget`

O Gemini tem duas convenções incompatíveis: o **2.5** só aceita `thinking_budget`
(em tokens) e o **3.x** só aceita `thinking_level` (`LOW`/`HIGH`) — misturar dá
HTTP 400. A jangada resolve por você: passe **`thinking_budget`** (ou
`thinking_level`) e a lib adapta ao modelo, empacotando no `thinking_config`
nativo por baixo dos panos.

```python
# Funciona igual nas duas versões — você não muda nada:
LLM("gemini", "gemini-2.5-flash").complete("...", params={"thinking_budget": 1024})
LLM("gemini", "gemini-3-pro").complete("...",  params={"thinking_budget": 1024})
# no 2.5 vira thinking_config(thinking_budget=1024);
# no 3.x o perfil converte para thinking_config(thinking_level="HIGH").
```

- `thinking_budget`: `0` desliga (quando o modelo permite), `-1` é automático.
- No 3.x o budget é aproximado para um nível válido (`LOW` se ≤0, senão `HIGH`);
  no 2.5 um `thinking_level` é convertido para budget. Um `thinking_config` pronto
  é respeitado como veio.

## Por que é o "canivete suíço" aqui

É o único que cobre vision, detecção e áudio **sem endpoints separados** —
tudo via `generateContent`. Veja [Matriz de capacidades](capabilities.md).
