# Melhores práticas

Um apanhado de recomendações para tirar o máximo da jangada em produção. Cada
item aponta para o guia detalhado da capacidade correspondente.

## Provider e modelo

- **Troque por configuração, não por código.** Mantenha `provider`, `model` e
  `api_key` em variáveis de ambiente. A promessa da lib é trocar o provider sem
  mexer no resto — aproveite isso para alternar entre ambientes (dev/prod) e
  fazer testes A/B de modelo.
- **Use o modelo certo para cada tarefa.** Um modelo forte para raciocínio/escrita
  e um modelo barato (ex.: `llama-3.1-8b-instant`) para classificação, triagem e
  judges de guardrail. Não pague por capacidade que a tarefa não exige.
- **Deixe os perfis normalizarem os params.** Não escreva `if model == ...` para
  ajustar `temperature`/`max_tokens`: a camada de perfis já adapta o payload por
  modelo (ver [Parâmetros](parameters.md)).

> **Nota:** sempre defina `max_tokens` explicitamente em extrações longas.
> Modelos com *thinking* (ex.: Gemini 2.5) podem consumir o orçamento de saída e
> truncar o JSON — um `max_tokens` folgado evita respostas cortadas.

## Structured output

- **Valide sempre contra o schema.** Use `parse()`/`aparse()` com um modelo
  Pydantic; não confie em parsing manual de texto.
- **Tenha um fallback de coerção.** Em alguns SDKs `completion.parsed` pode vir
  `None` mesmo com JSON válido em `completion.text`. Caia para
  `Model.model_validate_json(completion.text)` nesse caso.
- Campos opcionais com `default=None` evitam que o modelo invente valores quando
  o dado não existe. Veja [Structured output](structured-output.md).

## Guardrails

- **Cheque o escopo na entrada, uma vez.** Em agentes com loop de ferramentas,
  não coloque o `ScopeGuard` no LLM que itera — a cada passo o histórico cresce e
  a reavaliação pode recusar uma fala válida. Faça a checagem com um LLM
  "porteiro" antes de iniciar o agente.
- **Use `raise_on_block=True`** quando quiser tratar a recusa no seu fluxo (ex.:
  responder com uma mensagem própria) em vez de devolver a `Completion` de recusa.
- **`fail_closed=True`** em domínios sensíveis: se o judge falhar, barra (seguro).
  Deixe `False` quando disponibilidade importa mais que rigor.
- Reserve a **blocklist** para termos óbvios (regex, custo zero) e deixe o
  **judge** decidir o escopo semântico. Veja [Guardrails](guardrails.md).

## RAG

- **Comece com busca híbrida** (`mode="hybrid"`): combina vetorial e BM25 por RRF
  e costuma superar só vetorial em perguntas com termos exatos.
- **Use `task="document"` ao indexar e `task="query"` ao buscar** — alguns
  providers (Gemini) diferenciam, e o orquestrador `RAG` já faz isso por você.
- **Amplie a recuperação com step-back.** Para perguntas muito específicas, gere
  uma pergunta mais ampla com [`step_back()`](stepback.md) e busque com as duas —
  recupera contexto de fundo que a query original sozinha perderia.
- **Deixe um agente decidir quando recuperar.** Nem toda mensagem precisa de RAG:
  exponha a busca como uma ferramenta e deixe o modelo chamá-la só quando a
  pergunta exigir contexto — saudações e conversa não devem disparar a base.
- Ajuste `k`, `min_score` e `chunk` ao seu conteúdo. Veja [RAG](rag.md).

## Retry e fallback

- **Configure retry para erros transitórios** (429, 5xx, timeouts) com backoff e
  `jitter=True`. Não faça failover em erros de auth (401/403) ou bad request
  (400/422) — trocar de provider não resolve.
- **Encadeie um fallback barato → forte → alternativo** com `with_fallback`. O
  failover acontece antes do primeiro token, inclusive em streaming.
- Veja [Retry e fallback](retry-fallback.md) e [Erros](errors.md).

## Custo e observabilidade

- **Leia `usage` e `cost`** em cada resposta e agregue por fluxo (`Flow`/`Graph`
  somam automaticamente). Sobrescreva preços com `register_price` conforme seu
  contrato.
- **Agrupe chamadas num `Trace`.** Uma requisição do seu serviço = um lote de
  observações (detecção, extração, conferência...), facilitando auditoria e
  diagnóstico. Veja [Custo](cost.md) e [Observabilidade](observability.md).

## Agentes e ferramentas

- **Descreva bem cada ferramenta.** O docstring é o que o modelo lê para decidir
  quando chamá-la — diga o que faz e *quando (não) usar*.
- **Force aritmética via tool.** Para somas/contas, use `tool_choice="required"`
  numa ferramenta de cálculo em vez de confiar na conta "de cabeça" do modelo.
- **Limite `max_iterations`** em agentes para evitar loops longos, e prefira
  `Squad` sequencial quando os papéis são claros (pesquisar → analisar → redigir).
- Veja [Tools](tools.md) e [Agentes](agents.md).

## Transcrição (áudio e vídeo)

- **O Whisper aceita vídeo, mas tem teto de tamanho.** Os endpoints de STT
  (OpenAI/Groq) transcrevem `mp4` direto — extraem a faixa de áudio sozinhos —,
  porém há um limite de **~25 MB** por arquivo. Um vídeo de reunião estoura isso
  com facilidade.
- **Pré-processe a mídia no seu serviço, não na lib.** Antes de transcrever,
  extraia só o áudio e normalize para algo leve (mono, 16 kHz, comprimido) com
  `ffmpeg`. Isso cabe no limite, acelera o upload e padroniza o container.
  Mantenha essa etapa no **seu backend**: a jangada é fina de propósito e não
  embute dependências de sistema (como `ffmpeg`) — ela só repassa os bytes ao
  provider via `Audio.from_bytes(dados, mime, name=...)`.
- **Preserve a extensão no `name`.** O Whisper usa o nome do arquivo para inferir
  o container; ao reprocessar, devolva algo como `reuniao.mp3`.
- **Tenha um fallback.** Se o `ffmpeg` não estiver disponível (ou falhar num
  codec exótico), mande o arquivo original — um `mp4` pequeno ainda transcreve.
- Veja [Transcrição de áudio](audio.md).

## Async e FastAPI

- Use `acomplete`/`aparse`/`astream` em handlers async. Para o pipeline síncrono
  (parsing de arquivos, chamadas em lote), rode em thread
  (`anyio.to_thread.run_sync`) para não bloquear o event loop.
- Em streaming, devolva um `StreamingResponse` consumindo o `astream`. Veja
  [Streaming](streaming.md).

> **Atenção:** não exponha suas chaves no front-end. O navegador deve falar com o
> **seu** backend; é o backend que detém as `api_key` dos providers.
