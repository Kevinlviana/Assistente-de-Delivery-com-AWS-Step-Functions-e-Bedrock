"""
Lambda: ConsultarCardapio
Busca os itens do pedido na tabela de cardapio (DynamoDB) para confirmar
disponibilidade e obter o preco atualizado de cada item.
"""
import os
import boto3
from boto3.dynamodb.conditions import Key

TABLE_NAME = os.environ.get("CARDAPIO_TABLE", "delivery-cardapio")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):
    itens = event.get("validacao", {}).get("itens_normalizados", [])

    encontrados = []
    indisponiveis = []

    for item_nome in itens:
        resp = table.query(
            KeyConditionExpression=Key("nome").eq(item_nome)
        )
        registros = resp.get("Items", [])

        if registros and registros[0].get("disponivel", True):
            item = registros[0]
            encontrados.append({
                "nome": item["nome"],
                "preco": float(item["preco"]),
            })
        else:
            indisponiveis.append(item_nome)

    total = sum(i["preco"] for i in encontrados)

    return {
        "itens": encontrados,
        "indisponiveis": indisponiveis,
        "subtotal": round(total, 2),
    }
