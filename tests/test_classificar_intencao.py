"""
Teste unitario para a Lambda ClassificarIntencao.
Usa mock do cliente Bedrock para nao depender de credenciais reais da AWS.
"""
import json
import sys
import os
from unittest.mock import patch, MagicMock

os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src/classificar_intencao"))

import app  # noqa: E402


def _mock_bedrock_response(intencao="novo_pedido", itens=None, pedido_id=None):
    corpo = {
        "content": [
            {
                "text": json.dumps({
                    "intencao": intencao,
                    "itens": itens,
                    "pedido_id": pedido_id,
                })
            }
        ]
    }
    mock_body = MagicMock()
    mock_body.read.return_value = json.dumps(corpo).encode("utf-8")
    return {"body": mock_body}


@patch("app.bedrock")
def test_classifica_novo_pedido(mock_bedrock):
    mock_bedrock.invoke_model.return_value = _mock_bedrock_response(
        intencao="novo_pedido", itens=["pizza margherita", "coca-cola"]
    )

    evento = {"mensagem": "Quero uma pizza margherita e uma coca-cola"}
    resultado = app.lambda_handler(evento, None)

    assert resultado["intencao"] == "novo_pedido"
    assert "pizza margherita" in resultado["itens"]


@patch("app.bedrock")
def test_fallback_para_duvida_geral_se_intencao_invalida(mock_bedrock):
    mock_bedrock.invoke_model.return_value = _mock_bedrock_response(intencao="algo_invalido")

    evento = {"mensagem": "blablabla"}
    resultado = app.lambda_handler(evento, None)

    assert resultado["intencao"] == "duvida_geral"


@patch("app.bedrock")
def test_consulta_status_extrai_pedido_id(mock_bedrock):
    mock_bedrock.invoke_model.return_value = _mock_bedrock_response(
        intencao="consultar_status", pedido_id="PED123"
    )

    evento = {"mensagem": "Qual o status do pedido PED123?"}
    resultado = app.lambda_handler(evento, None)

    assert resultado["intencao"] == "consultar_status"
    assert resultado["pedido_id"] == "PED123"
