"""Ollama (API nativa): modelos locais — texto, streaming, structured, tools, embeddings.

Pré-requisitos (local, sem chave):
    ollama serve                 # servidor em http://localhost:11434
    ollama pull llama3.2         # chat
    ollama pull embeddinggemma   # embeddings (opcional)

Instale: pip install "jangada-ai[ollama]"

Host: host= no construtor > env OLLAMA_HOST > http://localhost:11434.
Ollama Cloud: LLM("ollama", "gpt-oss:120b", host="https://ollama.com") com
OLLAMA_API_KEY no ambiente (structured output não funciona na Cloud, hoje).
"""
from pydantic import BaseModel

from jangada_ai import LLM, Message

# num_ctx (janela de contexto) e keep_alive são nativos do Ollama -> extra=.
llm = LLM("ollama", "llama3.2", temperature=0.2,
          extra={"num_ctx": 8192, "keep_alive": "10m"})

# Texto.
print(llm.complete("Diga olá em português, só uma palavra.").text)

# Streaming (usage chega no último chunk -> llm.provider.last_stream).
for pedaco in llm.stream("Conte de 1 a 5 separado por vírgula."):
    print(pedaco, end="", flush=True)
print("\n", llm.provider.last_stream["usage"])


# Structured output (format = JSON Schema do modelo Pydantic).
class Pais(BaseModel):
    nome: str
    capital: str


print(llm.parse("Fale do Brasil.", Pais).parsed)


# Function calling (o resultado volta como role="tool" + tool_name).
def clima(cidade: str) -> str:
    """Retorna o clima atual da cidade."""
    return f"Ensolarado em {cidade}"


comp = llm.complete("Como está o clima em Recife?", tools=[clima])
if comp.tool_calls:
    call = comp.tool_calls[0]
    hist = [Message("user", "Como está o clima em Recife?"), comp.assistant_message(),
            Message.tool_results(call.result(clima(**call.args)))]
    print(llm.complete(None, history=hist, tools=[clima]).text)

# Thinking (modelos com raciocínio, ex.: qwen3, deepseek-r1, gpt-oss):
#   r = LLM("ollama", "qwen3", extra={"think": True}).complete("...")
#   r.text -> resposta final; r.raw.message.thinking -> raciocínio

# Embeddings (em lotes).
try:
    emb = LLM("ollama", "embeddinggemma")
    print(len(emb.embed("jangada é uma embarcação")), "dimensões")
except Exception as e:  # modelo de embedding não baixado
    print("embeddings:", e)
