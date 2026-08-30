"""
Lambda: ClassificarIntencao
Recebe a mensagem em linguagem natural do cliente e usa o Amazon Bedrock
(Claude) para classificar a intencao em uma categoria fixa, retornando
JSON estruturado. O modelo NAO decide regras de negocio, apenas
interpreta linguagem.
"""
import json
import os
import boto3

MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")

bedrock = boto3.client("bedrock-runtime")

INTENCOES_VALIDAS = {"novo_pedido", "consultar_status", "cancelar", "duvida_geral"}

SYSTEM_PROMPT = """Voce e um classificador de intencoes para um assistente de delivery.
Dada a mensagem do cliente, classifique em EXATAMENTE uma das opcoes:
- novo_pedido: cliente quer fazer um pedido novo
- consultar_status: cliente quer saber o status de um pedido existente
- cancelar: cliente quer cancelar um pedido
- duvida_geral: qualquer outra coisa (perguntas, saudacoes, reclamacoes gerais)

Se for novo_pedido, extraia tambem os itens mencionados em uma lista simples de strings.
Se for consultar_status ou cancelar, extraia o numero/id do pedido se mencionado (ou null).

Responda APENAS com um JSON valido, sem nenhum texto adicional, no formato:
{"intencao": "...", "itens": [...] ou null, "pedido_id": "..." ou null}
"""


def lambda_handler(event, context):
    mensagem = event.get("mensagem", "")

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 300,
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": mensagem}
        ],
    }

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json",
    )

    payload = json.loads(response["body"].read())
    texto = payload["content"][0]["text"].strip()

    try:
        resultado = json.loads(texto)
    except json.JSONDecodeError:
        # fallback defensivo caso o modelo devolva algo fora do formato esperado
        resultado = {"intencao": "duvida_geral", "itens": None, "pedido_id": None}

    if resultado.get("intencao") not in INTENCOES_VALIDAS:
        resultado["intencao"] = "duvida_geral"

    return resultado
