"""Step-back prompting: gera uma pergunta conceitualmente mais ampla.

A partir de uma pergunta específica, o modelo abstrai um passo "para trás" e
formula uma pergunta mais geral — útil para, num RAG, recuperar documentos de
contexto amplo além dos trechos específicos. Funciona em qualquer provider.
"""
from jangada_ai import LLM, step_back

llm = LLM("openai", "gpt-4o-mini")   # ou ("gemini", "gemini-2.5-flash"), etc.

# 1) Geração simples
pergunta = "Quais são as opções de tratamento para catarata?"
ampla = step_back(llm, pergunta)
print("Original:", pergunta)
print("Step-back:", ampla)

# 2) Fixando domínio/idioma via instructions
ampla_med = step_back(
    llm,
    "Como configurar retry e fallback no jangada?",
    instructions="Contexto: bibliotecas de software. Responda em pt-BR.",
)
print("Step-back (com instructions):", ampla_med)

# 3) Padrão de uso com RAG: buscar com as DUAS perguntas e unir o contexto
# (requer pip install "jangada-ai[rag]")
#
#   from jangada_ai.rag import RAG, vector_store
#   rag = RAG(LLM("openai", "text-embedding-3-small"), vector_store("..."), chat=llm)
#   especificos = rag.search(pergunta)
#   gerais = rag.search(ampla)
#   # deduplique especificos + gerais e responda com o contexto unido.
