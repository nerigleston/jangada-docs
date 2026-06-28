"""AWS Bedrock via Converse API (boto3): texto, structured e streaming.

Credenciais: a cadeia padrão do boto3 (AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY,
perfil ~/.aws, role da instância...). Região via AWS_REGION ou region_name=.
O `model` é o id do modelo ou do inference profile do Bedrock.

Instale: pip install "jangada-ai[bedrock]"
"""
import asyncio

from pydantic import BaseModel

from jangada_ai import LLM

# Ex.: um inference profile cross-region do Claude no Bedrock.
llm = LLM("bedrock", "us.anthropic.claude-3-5-sonnet-20241022-v2:0", region_name="us-east-1")

# Texto.
print(llm.complete("Diga olá em português, só uma palavra.").text)

# Streaming (converse_stream).
for pedaco in llm.stream("Conte de 1 a 5 separado por vírgula."):
    print(pedaco, end="", flush=True)
print()


# Structured output (tool-forcing — funciona nos modelos que aceitam tool use).
class Fatura(BaseModel):
    fornecedor: str
    total: float


f = llm.parse("Extraia: Padaria do Zé, total R$26.", Fatura).parsed
print(f.fornecedor, f.total)


# Async (o SDK é sync; a jangada usa asyncio.to_thread por baixo).
async def main():
    comp = await llm.acomplete("Responda apenas: ok")
    print(comp.text)


asyncio.run(main())
