"""
Lambda: CancelarPedido
Cancela um pedido existente, se ainda estiver em um status cancelavel.
"""
import os
import boto3

TABLE_NAME = os.environ.get("PEDIDOS_TABLE", "delivery-pedidos")
STATUS_CANCELAVEIS = {"recebido", "em_preparo"}

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):
    pedido_id = event.get("classificacao", {}).get("pedido_id")

    if not pedido_id:
        return {"tipo": "cancelamento_falhou", "motivo": "pedido_nao_identificado"}

    resp = table.get_item(Key={"pedidoId": pedido_id})
    item = resp.get("Item")

    if not item:
        return {"tipo": "cancelamento_falhou", "motivo": "pedido_nao_encontrado", "pedido_id": pedido_id}

    if item.get("status") not in STATUS_CANCELAVEIS:
        return {
            "tipo": "cancelamento_falhou",
            "motivo": "status_nao_cancelavel",
            "pedido_id": pedido_id,
            "status_atual": item.get("status"),
        }

    table.update_item(
        Key={"pedidoId": pedido_id},
        UpdateExpression="SET #s = :novo_status",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":novo_status": "cancelado"},
    )

    return {"tipo": "cancelamento_confirmado", "pedido_id": pedido_id}
