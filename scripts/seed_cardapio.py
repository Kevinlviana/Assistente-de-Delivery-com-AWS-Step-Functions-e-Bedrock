"""
Popula a tabela DynamoDB de cardapio com itens de exemplo.
Uso: python scripts/seed_cardapio.py
"""
import boto3
import os

TABLE_NAME = os.environ.get("CARDAPIO_TABLE", "delivery-cardapio")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

ITENS = [
    {"nome": "pizza margherita", "preco": 42.90, "disponivel": True},
    {"nome": "pizza calabresa", "preco": 44.90, "disponivel": True},
    {"nome": "coca-cola", "preco": 8.00, "disponivel": True},
    {"nome": "suco de laranja", "preco": 9.50, "disponivel": True},
    {"nome": "hamburguer artesanal", "preco": 32.00, "disponivel": True},
    {"nome": "batata frita", "preco": 15.00, "disponivel": False},
]

if __name__ == "__main__":
    with table.batch_writer() as batch:
        for item in ITENS:
            batch.put_item(Item=item)
    print(f"{len(ITENS)} itens inseridos na tabela {TABLE_NAME}.")
