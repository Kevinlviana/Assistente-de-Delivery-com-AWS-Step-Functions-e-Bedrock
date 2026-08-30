# Diagrama de Arquitetura

> Este diagrama renderiza automaticamente na visualização do GitHub.

```mermaid
flowchart TD
    Cliente[Cliente] -->|POST /assistente| APIGW[API Gateway]
    APIGW --> SFN[Step Functions: delivery-assistant-flow]

    subgraph SFN["AWS Step Functions"]
        A[ClassificarIntencao<br/>Lambda + Bedrock] --> B{RotearIntencao}
        B -->|novo_pedido| C[ValidarPedido]
        C --> D[Parallel]
        D --> D1[ConsultarCardapio<br/>DynamoDB]
        D --> D2[CalcularFrete]
        D1 --> E[ConfirmarPedido]
        D2 --> E
        B -->|consultar_status| F[ConsultarStatus<br/>DynamoDB]
        B -->|cancelar| G[CancelarPedido<br/>DynamoDB]
        B -->|duvida_geral| H[RespostaGenerica]
        E --> I[GerarRespostaNatural<br/>Lambda + Bedrock]
        F --> I
        G --> I
        H --> I
    end

    I --> Resposta[Resposta ao cliente]
    Resposta --> Cliente
```

## Fluxo de dados

1. O cliente envia uma mensagem em linguagem natural via API Gateway.
2. `ClassificarIntencao` chama o Amazon Bedrock (Claude) para transformar
   texto livre em uma intenção estruturada (`novo_pedido`,
   `consultar_status`, `cancelar` ou `duvida_geral`).
3. O estado `Choice` roteia a execução para o ramo correto.
4. Cada ramo executa lógica de negócio **determinística** (validação,
   consulta a banco de dados, cálculo de frete) — sem envolver o modelo.
5. O resultado estruturado de qualquer ramo converge para
   `GerarRespostaNatural`, que usa o Bedrock novamente, agora só para
   transformar o resultado em uma resposta em linguagem natural.
6. A resposta final volta ao cliente via API Gateway.
