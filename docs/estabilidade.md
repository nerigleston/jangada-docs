# Estabilidade da API (público × interno)

Nem tudo na jangada tem o mesmo nível de garantia. Esta página classifica a API
em **Estável** (coberta pela [política de versionamento](semver.md)) e
**Experimental** (pode mudar sem o ciclo de deprecação).

## Como saber o que é público

A API pública é o que está exportado em `jangada_ai.__all__` (o que você importa
direto de `jangada_ai`). Qualquer coisa **não** listada lá — submódulos internos,
nomes com `_` no início, atributos `raw`, detalhes dos adapters — é **interno** e
pode mudar a qualquer momento.

```python
import jangada_ai
print(jangada_ai.__all__)   # a superfície pública
```

## Estável

Coberto pela garantia de SemVer (sem breaking em minor/patch após o 1.0; com
ciclo de `DeprecationWarning` antes de qualquer quebra):

| Área | Símbolos |
|------|----------|
| Cliente | `LLM` (`complete`/`acomplete`, `parse`/`aparse`, `stream`/`astream`, retry, fallback, `embed`) |
| Tipos da fronteira | `Message`, `Completion`, `Image`, `ImagePart`, `TextPart`, `Audio`, `AudioPart` |
| Tools | `Tool`, `to_tool`, `ToolCall`, `ToolCallPart`, `ToolResultPart` |
| Orquestração | `Flow`, `Step`, `FlowResult`, `Graph`, `GraphResult` |
| Templates | `Template` |
| Erros | módulo `errors` (hierarquia `LLMError` e subclasses, `classify`, `TRANSIENT`, `DEFAULT_FAILOVER`) |
| Documentos | `Document`, `DocumentError` |
| Providers | `Provider`, `register`, `available_providers` (contrato de extensão) |
| Config | `load_env` |

Os **providers** `anthropic`, `openai`, `groq`, `gemini` são estáveis. Os novos
`azure`, `bedrock`, `vertex` e `openrouter` são estáveis no contrato (os 6
métodos), mas dependem de SDKs de terceiros cujos modelos/endpoints mudam — veja
`maintenance/`.

## Experimental

Funciona e é testado, mas a API pode mudar entre versões sem aviso formal
(podemos ajustar assinaturas conforme o ecossistema evolui):

| Área | Símbolos | Por quê |
|------|----------|---------|
| Agentes/times | `Agent`, `Squad`, `RAGMemory`, `plan` (+ A2A) | superfície grande, em evolução |
| MCP | `MCPClient`, `MCPServer`, `run_agent`, `serve_mcp`, `build_mcp_server`, `build_mcp_app` | acompanha o protocolo MCP (beta nos SDKs) |
| Guardrails | `ScopeGuard`, `Guardrail`, `GuardResult` | heurísticas em ajuste |
| Cache | `Cache`, `ExactCache`, `SemanticCache` | |
| RAG | módulo `jangada_ai.rag` (chunking, vector stores, reranking, estratégias) | módulo opcional, em expansão |
| Observability/Eval/Prompts | `observability_session`, `feedback`, `PromptVersion`, `Evaluator`/`Dataset`/`evaluate` | dependem do backend/painel |
| Detecção/Step-back | `detect_objects(_full)`, `step_back` | utilitários compostos |
| Preços/Perfis | `pricing.*`, `profiles.*` (`register_price`, `apply_profile`, ...) | tabelas aproximadas, mudam com o mercado |

## Regra prática

- Construindo algo de produção sobre o **núcleo** (`LLM` + tipos + flow + erros)?
  Pode confiar na estabilidade.
- Usando agentes/MCP/RAG/eval? Ótimo — só **fixe a versão** (`jangada-ai==X.Y.*`)
  e leia o [CHANGELOG](../CHANGELOG.md) ao subir de versão.
