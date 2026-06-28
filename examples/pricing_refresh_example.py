"""Preços dinâmicos: a tabela se atualiza sozinha, sem dar `pip install -U`.

A jangada embute uma tabela de preços (fallback offline). Por PADRÃO, na primeira
vez que ela calcula um custo (logo abaixo de cada chamada de provider), dispara em
BACKGROUND um refresh do catálogo publicado, cacheado por 1 dia — o usuário não
precisa escrever nada. Este exemplo mostra o controle MANUAL (`refresh_prices`),
útil para garantir preços frescos de forma síncrona (ex.: no boot).

Custos continuam sendo ESTIMATIVA aproximada, não billing.
"""
import jangada_ai

# 1) Custo com a tabela EMBUTIDA (sempre disponível, offline).
print("preço embutido gpt-4o-mini:", jangada_ai.price_for("gpt-4o-mini"))

# 2) AUTOMÁTICO: você não precisa fazer nada. Basta usar o LLM normalmente — o
#    primeiro Completion.cost já dispara o refresh em background (cache 1 dia).
#    Desligue com a env JANGADA_NO_PRICE_REFRESH=1.

# 3) MANUAL (opcional): força o refresh agora, de forma síncrona.
#    - URL padrão embutida (https://jangada.dev.br/prices.json); não precisa de .env.
#    - cacheia em ~/.cache/jangada/prices.json por 24h (ttl configurável).
#    - se a rede falhar, cai pro cache e depois pro embutido — nunca levanta.
atualizou = jangada_ai.refresh_prices()       # opcional: url=, ttl=, timeout=, force=
print("pegou preços remotos?" , atualizou)
print("preço (pós-refresh) gpt-4o-mini:", jangada_ai.price_for("gpt-4o-mini"))

# 3) Daqui pra frente, todo Completion já vem com .cost usando a tabela atualizada.
#    (exige chave/SDK do provider — descomente para rodar de verdade)
# llm = jangada_ai.LLM(provider="openai", model="gpt-4o-mini")
# comp = llm.complete("Diga olá em uma palavra.")
# print("custo estimado desta chamada (USD):", comp.cost)

# Override manual continua valendo e vence tudo (caso queira um preço exato):
jangada_ai.register_price(r"gpt-4o-mini", 0.99, 1.99)
print("após override manual:", jangada_ai.price_for("gpt-4o-mini"))
