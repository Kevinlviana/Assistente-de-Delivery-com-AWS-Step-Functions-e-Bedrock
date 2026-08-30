# 🍔 Delivery Assistant — Step Functions + Amazon Bedrock

Assistente virtual serverless para delivery, que interpreta mensagens em
linguagem natural, orquestra a lógica de pedidos com **AWS Step Functions**
e usa **Amazon Bedrock (Claude)** tanto para classificar a intenção do
cliente quanto para gerar respostas humanizadas.

> Diagrama completo em [`docs/arquitetura.md`](docs/arquitetura.md) (renderiza direto no GitHub via Mermaid).

## ✨ O que o projeto demonstra

- Orquestração de um fluxo de negócio real com **Step Functions** (Choice,
  Parallel, Retry/Catch)
- Uso de **LLMs (Bedrock)** em dois papéis distintos e bem separados:
  - **Classificação de intenção** (NLU) — decide o caminho no fluxo
  - **Geração de linguagem natural** — traduz o resultado estruturado da
    lógica de negócio numa resposta simpática para o cliente
- Separação clara entre **decisão de negócio** (código determinístico) e
  **interpretação de linguagem** (LLM) — o modelo nunca decide preço,
  estoque ou regras de negócio
- Infraestrutura como código com **AWS SAM**
- Persistência em **DynamoDB**
- Notificação assíncrona via **SNS**

## 🏗️ Arquitetura

```
Cliente (API Gateway)
        │
        ▼
  Lambda "Entrada"
        │
        ▼
┌─────────────────────────── Step Functions ───────────────────────────┐
│                                                                        │
│   ClassificarIntencao (Bedrock)                                       │
│            │                                                          │
│            ▼                                                          │
│   RotearIntencao (Choice)                                             │
│      ├── novo_pedido ─▶ ValidarPedido ─▶ ConsultarCardapio            │
│      │                        │                                       │
│      │                        ▼                                      │
│      │                  CalcularFrete (Parallel c/ ConsultarEstoque)  │
│      ├── consultar_status ─▶ ConsultarStatus                          │
│      ├── cancelar ─▶ CancelarPedido                                   │
│      └── duvida_geral ─▶ RespostaGenerica                             │
│            │                                                          │
│            ▼                                                          │
│   GerarRespostaNatural (Bedrock)                                      │
│            │                                                          │
│            ▼                                                          │
│   Notificar (SNS) [opcional / async]                                  │
│                                                                        │
└────────────────────────────────────────────────────────────────────┘
        │
        ▼
  Resposta ao cliente (JSON)
```

## 📁 Estrutura do repositório

```
delivery-assistant/
├── statemachine/
│   └── delivery.asl.json        # Definição do Step Functions
├── src/
│   ├── classificar_intencao/    # Lambda: chama Bedrock p/ NLU
│   ├── validar_pedido/          # Lambda: valida payload do pedido
│   ├── consultar_cardapio/      # Lambda: busca itens no DynamoDB
│   ├── calcular_frete/          # Lambda: regra de negócio de frete
│   ├── consultar_status/        # Lambda: status de pedido existente
│   ├── cancelar_pedido/         # Lambda: cancela pedido
│   └── gerar_resposta/          # Lambda: chama Bedrock p/ resposta natural
├── infra/
│   └── template.yaml            # Infraestrutura AWS SAM
├── tests/
│   └── test_classificar_intencao.py
├── docs/
│   └── arquitetura.md            # Diagrama Mermaid
├── events/
│   └── exemplo-novo-pedido.json
├── requirements.txt
├── samconfig.toml
└── README.md
```

## 🚀 Como rodar

### Pré-requisitos
- AWS CLI configurado (`aws configure`)
- AWS SAM CLI instalado
- Python 3.12+
- Acesso habilitado ao modelo Claude no Amazon Bedrock (console → Bedrock →
  Model access)

### Deploy

O `template.yaml` fica em `infra/`, então aponte o SAM CLI para ele:

```bash
sam build -t infra/template.yaml
sam deploy --guided
```

### Popular o cardápio de exemplo

```bash
pip install boto3
python scripts/seed_cardapio.py
```

Na primeira execução, o `--guided` vai pedir nome do stack, região e
confirmar a criação de roles IAM. As execuções seguintes podem usar apenas
`sam deploy`.

### Testando a state machine

```bash
aws stepfunctions start-execution \
  --state-machine-arn <ARN_DA_STATE_MACHINE> \
  --input file://events/exemplo-novo-pedido.json
```

Ou visualize o fluxo rodando direto no console do Step Functions — a
visualização gráfica de cada execução é ótima para entender falhas e
retries.

### Testes unitários

```bash
pip install -r requirements.txt
pytest tests/
```

## 🧠 Decisões de design

- **Por que Step Functions em vez de tudo em uma Lambda só?**
  O fluxo tem múltiplos passos com naturezas diferentes (IA, validação,
  banco de dados, notificação), cada um com sua própria política de retry.
  Orquestrar com Step Functions dá visibilidade (histórico de execução no
  console), resiliência (retry/catch declarativos) e desacopla cada etapa,
  facilitando testes e evolução isolada.

- **Por que duas chamadas a Bedrock em vez de uma?**
  Separar "entender a intenção" de "gerar a resposta final" evita que o
  modelo tente fazer as duas coisas ao mesmo tempo (o que costuma gerar
  respostas inconsistentes) e permite trocar/otimizar cada prompt
  independentemente — por exemplo, usar um modelo mais rápido/barato para
  classificação e um mais capaz para a resposta final.

- **Custo estimado**: com uso baixo/moderado (ex: portfólio, testes,
  poucos milhares de execuções/mês), o custo fica dominado pelas chamadas
  ao Bedrock; Step Functions, Lambda e DynamoDB no free tier cobrem a
  maior parte de um cenário de demonstração.

## 📌 Possíveis evoluções

- Adicionar estado `Map` para processar múltiplos itens do pedido em
  paralelo
- Integrar um canal real (WhatsApp Business API / Telegram) na entrada
- Adicionar autenticação de cliente via Cognito
- Persistir histórico de conversa para dar contexto multi-turno ao Bedrock

## 📄 Licença

MIT
