# Cookbook — receitas end-to-end

Diferente de `examples/*.py` (que demonstram **uma** feature), o cookbook traz
**casos reais completos**, prontos pra rodar. Cada receita é um script com chaves
reais + um cabeçalho explicando o que faz.

| # | Receita | O que ensina | Precisa de |
|---|---|---|---|
| 01 | [Extração de nota fiscal](01_extracao_nota_fiscal.py) | vision + structured output (Pydantic) | `[openai]` + uma imagem |
| 02 | [Agente MCP](02_agente_mcp.py) | `MCPClient` + `run_agent` contra servidor MCP real | `[openai,mcp]` + URL MCP |
| 03 | [Chatbot RAG](03_chatbot_rag.py) | embeddings + busca híbrida (BM25+vetorial) + resposta | `[openai,rag]` |
| 04 | [Fallback multi-provider](04_fallback_multiprovider.py) | trocar provider + retry/fallback + custo | 2 providers |
| 05 | [Transcrição + resumo](05_transcricao_resumo.py) | áudio → texto → resumo encadeado (`Flow`) | `[groq,openai]` + áudio |
| 06 | [Observabilidade](06_observabilidade.py) | Automática (zero-config) + `observability_session` p/ agrupar | `JANGADA_OBSERVABILITY*` no `.env` |

## Como rodar

```bash
pip install "jangada-ai[all]"        # ou só os extras de cada receita
export OPENAI_API_KEY=sk-...         # as chaves que a receita usa
python examples/cookbook/01_extracao_nota_fiscal.py /caminho/nota.jpg
```

As chaves vêm do ambiente (ou de um `.env` na raiz, detectado na importação).
Cada receita imprime o que recebeu e o resultado — é pra ler **e** rodar.
