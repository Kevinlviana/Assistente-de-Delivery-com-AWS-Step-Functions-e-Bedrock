"""
Lambda: ValidarPedido
Valida a estrutura basica do pedido extraido pela etapa de classificacao
de intencao. Logica puramente determinística - sem chamadas a LLM aqui.
"""


class PedidoInvalidoError(Exception):
    pass


def lambda_handler(event, context):
    itens = event.get("classificacao", {}).get("itens")

    if not itens or not isinstance(itens, list) or len(itens) == 0:
        raise PedidoInvalidoError("Pedido sem itens validos")

    return {
        "valido": True,
        "itens_normalizados": [item.strip().lower() for item in itens]
    }
