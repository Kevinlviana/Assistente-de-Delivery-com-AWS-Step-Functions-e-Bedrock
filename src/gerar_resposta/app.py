"""
Lambda: GerarRespostaNatural
Recebe o resultado ESTRUTURADO da logica de negocio (ja processado pelas
outras etapas da state machine) e usa o Bedrock apenas para traduzir esse
resultado em uma resposta em linguagem natural, amigavel, para o cliente.
"""
import json
import os
import boto3

MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")

bedrock = boto3.client("bedrock-runtime")

SYSTEM_PROMPT = """Voce e o assistente virtual de um app de delivery, com tom simpatico,
direto e profissional. Voce vai receber um JSON com o resultado ja processado
de uma acao (pedido confirmado, status de pedido, cancelamento, erro, duvida geral).

Sua unica tarefa e transformar esse JSON em uma mensagem curta e natural para o
cliente, em portugues do Brasil. Nao invente informacoes que nao estao no JSON.
Nao use markdown. Responda apenas com o texto da mensagem final."""


def lambda_handler(event, context):
    resultado_negocio = event.get("resultadoNegocio", {})

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 300,
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": json.dumps(resultado_negocio, ensure_ascii=False)}
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

    return {"mensagem": texto}
