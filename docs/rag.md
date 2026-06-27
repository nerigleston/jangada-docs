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

### Busca textual em português (pgvector)

O `PgVectorStore` usa a configuração `'simple'` do Postgres por padrão (sem
stemming nem stopwords). Para conteúdo em **português**, passe
`text_config="portuguese"` — melhora a parte lexical da busca híbrida (stemming PT
+ stopwords):

```python
from jangada_ai.rag import vector_store

store = vector_store("postgresql://...", text_config="portuguese")
```

A config é fixada na **criação** da tabela (a coluna `tsv` é GENERATED), então
defina-a antes do primeiro `setup`. Vale qualquer `regconfig` do Postgres
(`english`, `spanish`, ...).

## Modos de busca

`mode="vector" | "text" | "hybrid"`:

- **vector** — só similaridade do embedding.
- **text** — lexical: **BM25** no store em memória (com `rank_bm25`; cai para
  contagem de termos sem ele) e full-text nativo no pgvector (`tsvector`) / Mongo (`$text`).
- **hybrid** — combina os dois por **Reciprocal Rank Fusion (RRF)**.

O balanço vetorial × lexical sai de `weights=(vetorial, texto)` ou do atalho
**`alpha`** (0 = só BM25/texto, 1 = só vetorial; `alpha` vira `weights=(alpha, 1-alpha)`):

```python
RAG(emb, store, chat=chat, alpha=0.5)   # equilíbrio; 0.0 = só BM25, 1.0 = só vetorial
```

```python
rag.search("backup incremental", k=5, mode="vector")   # só vetorial
rag.search("backup incremental", k=5, mode="hybrid")   # vetorial + texto (RRF)
```

## Reranking (maior salto de qualidade)

O retriever traz candidatos (bom *recall*), mas a ordem nem sempre é a melhor.
Um **reranker** — modelo treinado em "este trecho responde a esta pergunta?" —
reordena os candidatos e fica com os melhores. Em RAG é o maior ganho de
qualidade por esforço.

Com `reranker=`, o `RAG` busca **mais** candidatos (`fetch_k`, padrão `k*4`) e
reordena, devolvendo os `k` melhores:

```python
from jangada_ai.rag import RAG, Reranker, vector_store

rag = RAG(emb, vector_store("memory"), chat=chat, reranker=Reranker.cohere())
rag.ask("Como faço backup incremental?")   # busca k*4 e reordena para os k melhores
```

Construtores do `Reranker`:

- `Reranker.cohere(model="rerank-v3.5")` — Cohere Rerank (precisa de `cohere` e
  `COHERE_API_KEY`).
- `Reranker.voyage(model="rerank-2")` — Voyage Rerank (precisa de `voyageai` e
  `VOYAGE_API_KEY`).
- `Reranker.fn(lambda query, docs: [scores])` — qualquer scorer (ex.: um
  cross-encoder local ou um LLM seu).

Extra opcional: `pip install "jangada-ai[rerank]"`. Controle fino:
`RAG(..., reranker=..., fetch_k=40)`; por chamada, `rag.search(q, rerank=False)`
desliga e `rerank=OutroReranker` sobrescreve.

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
