# Mistral

Provider `mistral`. Adapter sobre o **SDK oficial `mistralai`** (não é o caminho
OpenAI-compat): texto, vision, streaming, structured output, function calling e
embeddings.

```bash
pip install "jangada-ai[mistral]"
```

- **`provider=`**: `"mistral"`
- **Chave**: env `MISTRAL_API_KEY` (ou `api_key=` no construtor).

```python
from jangada_ai import LLM

llm = LLM("mistral", "mistral-large-latest")
print(llm.complete("Olá!").text)
```

## Modelos

- `mistral-large-latest` — Large 3, general-purpose multimodal.
- `mistral-medium-latest` — Medium 3.5, frontier multimodal/agentic e coding.
- `mistral-small-latest` — Small 4, híbrido (instruct/reasoning/coding), barato/rápido.
- `ministral-8b-latest` / `ministral-3b-latest` — compactos com texto+visão.
- `codestral-latest` — código.
- `mistral-embed` — embeddings.
- `mistral-ocr-latest` — OCR / Document AI.
- `voxtral-mini-latest` — transcrição de áudio.

## O que faz

- **Texto** (`complete`/`acomplete`) via `chat.complete`/`complete_async`.
- **Streaming** (`stream`/`astream`) via `chat.stream`/`stream_async`.
- **Structured output** (`parse`): helper nativo `chat.parse(response_format=Modelo)`
  — aceita o modelo Pydantic direto e devolve `message.parsed` (igual ao `.parse`
  da OpenAI).
- **Tools** (`tools=`/`tool_choice=`): formato OpenAI (`tool_calls`). `tool_choice`
  aceita `auto`/`none`/`any`/`required` ou o nome de uma função (força a chamada).
- **Vision** (`images=`): chunks `image_url` (Pixtral/medium/large).
- **Embeddings** (`embed`/`aembed`) com `mistral-embed`.
- **OCR / Document AI** (`ocr`/`aocr`) com `mistral-ocr-latest`: PDF/imagem →
  markdown por página, bounding boxes e imagens extraídas. `source` aceita URL,
  caminho, bytes, `ImagePart` ou um dict `document` da API. Retorna um `OCRResult`
  (`.text` = markdown de todas as páginas; `.pages` com `markdown`/`images`/
  `dimensions`). `include_images=True` traz o base64 das imagens; `pages=[...]`
  limita as páginas.
- **Transcrição** (`transcribe`/`atranscribe`) com Voxtral (`voxtral-mini-latest`).

```python
ocr = LLM("mistral", "mistral-ocr-latest")
doc = ocr.ocr("https://arxiv.org/pdf/2310.06825.pdf")
print(doc.pages[0].markdown)

stt = LLM("mistral", "voxtral-mini-latest")
print(stt.transcribe("audio.mp3", language="pt").text)
```

## Sync e async

O SDK `mistralai` tem um **único cliente** com métodos sync e `*_async`
(`complete`/`complete_async`, etc.). A jangada reusa a mesma instância para os
dois caminhos — a interface é idêntica aos outros providers.

## Quirks

- **Params**: a Mistral usa `random_seed` (a jangada mapeia o canônico `seed`) e
  **não** tem `top_k` (descartado). `max_tokens`, `temperature`, `top_p`, `stop`
  passam direto.
- **Streaming**: o conteúdo incremental vem em `event.data.choices[0].delta.content`.
- **MCP server-side não é suportado** pela jangada no Mistral — use `MCPClient`/
  `run_agent` (client-side) ou os providers Anthropic/OpenAI/Groq. A Mistral tem
  conectores nativos (`beta.connectors`), não integrados aqui.
- **Import do SDK**: a v2 (`mistralai>=2`) usa `from mistralai.client import Mistral`;
  a v1 usa `from mistralai import Mistral`. A jangada tenta os dois.

Relacionado: [Matriz de capacidades](capabilities.md),
[Providers e chaves](providers.md), [Structured output](structured-output.md).
