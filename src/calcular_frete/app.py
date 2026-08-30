"""
Lambda: CalcularFrete
Regra de negocio simples de calculo de frete baseada em distancia/faixa.
Em um cenario real, integraria com uma API de geolocalizacao/logistica.
"""

FRETE_BASE = 6.90
FRETE_GRATIS_ACIMA_DE = 60.00


def lambda_handler(event, context):
    distancia_km = event.get("distancia_km", 3)

    if distancia_km <= 2:
        valor = 0.0
    elif distancia_km <= 5:
        valor = FRETE_BASE
    else:
        valor = FRETE_BASE + (distancia_km - 5) * 1.5

    return {
        "valor_frete": round(valor, 2),
        "tempo_estimado_min": 25 + int(distancia_km * 2),
    }
