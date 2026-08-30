"""
Lambda: ConsultarStatus
Busca o status atual de um pedido existente no DynamoDB.
"""
import os
import boto3

TABLE_NAME = os.environ.get("PEDIDOS_TABLE", "delivery-pedidos")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):
    pedido_id = event.get("classificacao", {}).get("pedido_id")

    if not pedido_id:
        return {
            "tipo": "status_nao_encontrado",
            "mensagem": "Nao consegui identificar o numero do pedido."
        }

    resp = table.get_item(Key={"pedidoId": pedido_id})
    item = resp.get("Item")

    if not item:
        return {
            "tipo": "status_nao_encontrado",
            "pedido_id": pedido_id
        }

    return {
        "tipo": "status_pedido",
        "pedido_id": pedido_id,
        "status": item.get("status", "desconhecido"),
        "tempo_estimado_min": item.get("tempoEstimadoMin"),
    }
