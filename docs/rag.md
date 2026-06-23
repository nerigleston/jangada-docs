# RAG (embeddings + busca vetorial/híbrida)

A jangada cobre as partes "de LLM" do RAG (embeddings + montar o contexto) e traz
um módulo `jangada_ai.rag` opcional com chunking, vector store (pgvector/Mongo)
e busca híbrida.

```bash
pip install "jangada-ai[rag]"   # psycopg (pgvector) + pymongo (Mongo)
```

## Embeddings (`embed`)

Capacidade opcional, igual ao áudio: **OpenAI e Gemini** suportam; **Anthropic e
Groq** levantam `UnsupportedError`.

```python
from jangada_ai import LLM

emb = LLM("openai", "text-embedding-3-small")   # ou ("gemini", "gemini-embedding-001")
emb.embed("uma frase")            # -> vetor (list[float])
emb.embed(["a", "b"])             # -> lista de vetores
emb.embed(textos, task="document")  # task: "document" ao indexar, "query" ao buscar
```

`task` vira `task_type` no Gemini (`RETRIEVAL_DOCUMENT`/`RETRIEVAL_QUERY`); a
OpenAI ignora. `dimensions` (OpenAI) / `output_dimensionality` (Gemini) vão via `**opts`.

| Provider | Embeddings? | Modelo típico |
|----------|:-----------:|---------------|
| OpenAI   | ✅ | `text-embedding-3-small` / `-large` |
| Gemini   | ✅ | `gemini-embedding-001` |
| Anthropic| ❌ | — (use Voyage/Cohere por fora) |
| Groq     | ❌ | — |

## Pipeline completo (`RAG`)

```python
from jangada_ai import LLM
from jangada_ai.rag import RAG, vector_store

emb  = LLM("openai", "text-embedding-3-small")
chat = LLM("openai", "gpt-4o-mini")

# o store é escolhido pela STRING DE CONEXÃO (só passe a sua DATABASE_URL_VECTOR)
store = vector_store("postgresql://user:senha@host:5432/db")   # ou "mongodb+srv://..."
rag = RAG(emb, store, chat=chat, k=5)   # k = nº de trechos no contexto (ajustável)

rag.add_document("manual.pdf", metadata={"fonte": "manual"})   # extrai -> chunk -> embed -> grava
resposta = rag.ask("Como faço backup?", mode="hybrid")          # usa o k do RAG
mais = rag.ask("Como faço backup?", k=10, mode="hybrid")        # override por chamada
print(resposta.text)
for s in resposta.sources:
    print(s.score, s.chunk.content[:80])
```

## Vector store por string de conexão

`vector_store(url)` detecta o adapter pelo esquema:

| URL | Adapter | Busca |
|-----|---------|-------|
| `postgresql://` / `postgres://` | pgvector (Postgres) | cosseno (`<=>`) + full-text (`tsvector`) |
| `mongodb://` / `mongodb+srv://` | MongoDB | Atlas `$vectorSearch` + `$text` (fallback cosseno client-side) |
| `memory` / `None` | em memória | cosseno + keyword (sem deps) |

As tabelas/coleções e índices são criados sozinhos no primeiro uso (`setup`).

## Modos de busca

`mode="vector" | "text" | "hybrid"`:

- **vector** — só similaridade do embedding.
- **text** — só full-text/keyword.
- **hybrid** — combina os dois por **Reciprocal Rank Fusion (RRF)**.

```python
rag.search("backup incremental", k=5, mode="vector")   # só vetorial
rag.search("backup incremental", k=5, mode="hybrid")   # vetorial + texto (RRF)
```

## Parâmetros ajustáveis

Definidos no `RAG(...)` (padrão) e/ou por chamada:

```python
rag = RAG(
    emb, store, chat=chat,
    k=5,                      # nº de trechos no contexto
    min_score=0.25,           # descarta trechos abaixo dessa similaridade
    max_context_chars=6000,   # orçamento do contexto (trunca o excedente)
    chunker=meu_chunker,      # função(text)->list[str] (troca o chunking padrão)
    rrf_k=60,                 # constante do RRF (híbrido)
    weights=(1.0, 0.5),       # pesos (vetorial, texto) no híbrido
    chunk_size=1000, overlap=200,
)

# filtro por metadata (escopar por documento/fonte/tenant) + override por chamada
rag.ask("backup?", k=8, filter={"fonte": "manual"}, min_score=0.3, mode="hybrid")
rag.search("backup?", filter={"tenant": "acme"}, mode="vector")
```

- **`filter`** vira `metadata @> ...` no pgvector e `$match` em `metadata.<chave>` no Mongo.
- **`min_score`** usa a similaridade real (cosseno no vetorial, rank no texto).
- **`max_context_chars`** corta os trechos que não couberem (mantém ao menos um).
- **`weights=(v, t)`** pondera os rankings vetorial e de texto na fusão RRF.

## Chunking

```python
from jangada_ai.rag import chunk_text
chunk_text(texto, size=1000, overlap=200)   # quebra sem cortar palavras
```

Relacionado: [Documentos](documents.md) (extração de texto reaproveitada no RAG)
e [Observabilidade](observability.md).

## Exemplo

[`examples/rag_example.py`](https://raw.githubusercontent.com/nerigleston/jangada-docs/main/examples/rag_example.py) — script executável.
