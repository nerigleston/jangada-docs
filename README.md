<p align="center">
  <img src="assets/logo-full.png" alt="Jangada AI" width="420">
</p>

# jangada — documentação

Documentação pública da lib **jangada** (no PyPI: [`jangada-ai`](https://pypi.org/project/jangada-ai/)),
uma camada fina e adaptável sobre os SDKs oficiais de LLM (Anthropic, OpenAI,
Groq, Gemini): troque provider/model/api_key sem mudar o resto do código.

> O código-fonte da lib é mantido em um repositório separado. Este repositório
> contém apenas a documentação e os arquivos `llms.txt` / `llms-full.txt` para
> consumo por LLMs.

## Instalação

```bash
pip install jangada-ai      # o pacote importado segue: import jangada
```

## Para LLMs

- [`llms.txt`](llms.txt) — índice curto e curado, com links para cada guia.
- [`llms-full.txt`](llms-full.txt) — toda a documentação concatenada, para um único fetch.

## Guias

- [Começando](docs/getting-started.md)
- [Providers e chaves](docs/providers.md)
- [Parâmetros e perfis](docs/parameters.md)
- [Structured output](docs/structured-output.md)
- [Vision](docs/vision.md)
- [Documentos (docx/pdf/csv/xlsx)](docs/documents.md)
- [Streaming](docs/streaming.md)
- [Retry e fallback](docs/retry-fallback.md)
- [Custo e tokens](docs/cost.md)
- [Erros normalizados](docs/errors.md)
- [Fluxos e Graph](docs/flows.md)
- [Debug](docs/debug.md)
- [Estendendo (novo provider)](docs/extending.md)
