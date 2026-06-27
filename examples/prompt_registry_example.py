"""Prompt registry (opt-in): versionar prompts e referenciá-los pelo nome.

Convive com prompt no código. Requer JANGADA_OBSERVABILITY_API_KEY (chave do
projeto) no .env — a mesma da observabilidade. Veja docs/prompts.md.
"""
from jangada_ai import LLM, PromptVersion

# 1) publica uma versão e marca como produção (também dá pra fazer pelo painel)
PromptVersion.push(
    "assistente-fiscal",
    "Você é um assistente fiscal objetivo. Responda sobre {{ tema }}.",
    tag="production",
)

# 2) puxa a versão de produção e renderiza o template
p = PromptVersion.pull("assistente-fiscal")
print(f"usando v{p.version} (tag={p.tag})")
prompt = p.render(tema="emissão de NF-e")

# 3) usa no complete normal — prompt no código continua valendo do mesmo jeito
resp = LLM("openai", "gpt-4o-mini").complete(prompt)
print(resp.text)
