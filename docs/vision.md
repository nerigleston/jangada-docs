# Vision (imagens)

Imagens entram como `ImagePart` (bytes + mime) e são traduzidas para o formato
nativo de cada SDK. Use sempre um modelo com visão.

```python
from jangada_ai import LLM, Image

llm = LLM("openai", "gpt-4o-mini")

# por caminho
llm.complete("O que aparece aqui?", images=["foto.jpg"])

# por bytes ou base64
img = Image.from_bytes(upload_bytes, "image/png")   # ou Image.from_base64
recibo = llm.parse("Extraia o total.", Recibo, images=[img]).parsed

# rotular cada imagem: tuplas (rótulo, imagem) -> TextPart(rótulo) antes de cada uma
llm.parse("Compare.", Comparacao, images=[("frente", img), ("verso", img2)])
```

Para controle total da ordem (vários blocos texto/imagem, multi-turno), monte
`history=[Message("user", [TextPart(...), ImagePart(...), ...])]` com `prompt=None`.

## Tradução por provider

| Provider     | Formato nativo                          |
|--------------|-----------------------------------------|
| OpenAI/Groq  | `image_url` com data URI                |
| Anthropic    | bloco `image` / `source` base64         |
| Gemini       | `types.Part.from_bytes`                 |

Apenas bytes circulam (use `Image.from_path/bytes/base64`). Combine com
[Structured output](structured-output.md) passando `images=` no `parse()`.

## Vision x Documentos

Para **docx/pdf/csv/xlsx**, prefira [Documentos](documents.md): por padrão a
jangada extrai o texto localmente (mais barato, funciona em modelo sem visão) e
só usa vision quando você força `mode="vision"` ou quando o PDF é escaneado.

## Exemplo

[`examples/vision_example.py`](https://raw.githubusercontent.com/nerigleston/jangada-docs/main/examples/vision_example.py) — script executável.
