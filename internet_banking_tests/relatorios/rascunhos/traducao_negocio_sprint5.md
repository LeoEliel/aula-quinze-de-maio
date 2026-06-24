# traducao_negocio_sprint5.md
# Passo 3 — Tradução para o Negócio (Sprint 5)
# Leonardo Eliel Dias da Silva

## O que é tradução para o negócio?

Um mutante de "insuficiência de suíte" significa que o código original tem uma regra
de negócio que os testes antigos não verificavam de forma eficaz. A tradução para o
negócio responde: **o que aconteceria com o cliente bancário se esse bug fosse para produção?**

Cada mutante é descrito em três itens:
- **Regra de negócio afetada** — o que o sistema deveria garantir
- **Entrada discriminante** — os dados exatos que ativariam o bug
- **Resposta esperada** — o que o sistema correto deve retornar

---

## Mutante 1 — `<` → `<=` (linha 156 do app.py)

### Código mutado

```python
# Original (correto):
if conta_origem["saldo"] < valor:   # rejeita apenas quando saldo É MENOR que valor

# Mutante (com bug):
if conta_origem["saldo"] <= valor:  # rejeita também quando saldo É IGUAL ao valor
```

### 1. Regra de negócio afetada

> **"O cliente pode transferir qualquer valor até o limite total do seu saldo."**

O banco deve permitir que o cliente use **todo o saldo disponível** em uma única
transferência. Um cliente com R$ 1.000,00 tem o direito de transferir exatamente
R$ 1.000,00 — encerrando a conta com saldo zero.

Com o mutante ativo, o sistema passaria a exigir que o cliente sempre mantenha
**algum saldo residual** — uma restrição que não existe na regra de negócio e que
nunca foi comunicada ao cliente.

### 2. Entrada discriminante

| Campo | Valor |
|---|---|
| Endpoint | `POST /transferencia` |
| origem | `1` (Alice — saldo R$ 1.000,00) |
| destino | `2` (Bob) |
| valor | `1000.00` |

Condição exata: **saldo da conta de origem é igual ao valor transferido**.

### 3. Resposta esperada

| Sistema | HTTP | Body |
|---|---|---|
| **Original (correto)** | `200 OK` | `{"mensagem": "Transferencia realizada", "valor": 1000.0}` |
| **Mutante (com bug)** | `422` | `{"erro": "Saldo insuficiente", "saldo_atual": 1000.0}` |

**Impacto real:** O cliente ligaria para o suporte dizendo que tentou transferir
todo o seu saldo e o banco recusou, informando que o saldo era "insuficiente" —
mesmo com o valor exato disponível. Seria um bug de atendimento e reputação,
pois o sistema estaria mentindo para o cliente sobre seu próprio extrato.

---

## Mutante 2 — `==` → `!=` (linha 139 do app.py)

### Código mutado

```python
# Original (correto):
if origem == destino:   # bloqueia quando as contas SÃO IGUAIS

# Mutante (com bug):
if origem != destino:   # bloqueia quando as contas SÃO DIFERENTES
```

### 1. Regra de negócio afetada

> **"Não é permitido transferir dinheiro de uma conta para ela mesma."**

E, como consequência lógica da inversão: **toda transferência legítima entre
contas distintas passaria a ser bloqueada**.

Este é o mutante de maior gravidade — ele não apenas abre uma brecha (permitir
auto-transferência), como **torna o sistema de transferências completamente
inoperante** para qualquer par de contas distintas.

### 2. Entrada discriminante

Há dois casos que expõem o bug:

**Caso A — transferência bloqueada ilegitimamente:**

| Campo | Valor |
|---|---|
| Endpoint | `POST /transferencia` |
| origem | `1` (Alice) |
| destino | `2` (Bob) |
| valor | `100.00` |

**Caso B — auto-transferência permitida:**

| Campo | Valor |
|---|---|
| Endpoint | `POST /transferencia` |
| origem | `1` (Alice) |
| destino | `1` (Alice — mesma conta) |
| valor | `100.00` |

### 3. Resposta esperada

**Caso A (transferência legítima):**

| Sistema | HTTP | Body |
|---|---|---|
| **Original (correto)** | `200 OK` | `{"mensagem": "Transferencia realizada", "valor": 100.0}` |
| **Mutante (com bug)** | `422` | `{"erro": "Origem e destino nao podem ser iguais"}` |

**Caso B (mesma conta):**

| Sistema | HTTP | Body |
|---|---|---|
| **Original (correto)** | `422` | `{"erro": "Origem e destino nao podem ser iguais"}` |
| **Mutante (com bug)** | `200 OK` | `{"mensagem": "Transferencia realizada", "valor": 100.0}` |

**Impacto real (Caso A):** 100% dos clientes seriam impedidos de realizar qualquer
transferência. O sistema retornaria "Origem e destino não podem ser iguais" para
contas claramente distintas. O banco ficaria inoperante.

**Impacto real (Caso B):** Um cliente poderia transferir dinheiro para si mesmo
indefinidamente. Embora o saldo líquido não mude, o histórico de transferências
seria corrompido com operações falsas, e sistemas de compliance/auditoria poderiam
interpretar o volume de transações como atividade suspeita (lavagem de dinheiro).

---

## Mutante 3 — `<= 0` → `< 0` (linha 135 do app.py)

### Código mutado

```python
# Original (correto):
if not isinstance(valor, (int, float)) or valor <= 0:   # rejeita zero e negativos

# Mutante (com bug):
if not isinstance(valor, (int, float)) or valor < 0:    # rejeita apenas negativos
```

### 1. Regra de negócio afetada

> **"Toda transferência deve envolver um valor estritamente positivo."**

Uma transferência de R$ 0,00 não movimenta dinheiro algum. Ela consome recursos
do banco (conexão ao banco de dados, registro na tabela de transferências, processamento),
sem nenhum resultado financeiro. Aceitar valor zero:

- Cria registros fantasmas no histórico (`SELECT * FROM transferencias` retorna ruído)
- Abre precedente para automação maliciosa que envia milhares de requisições com `valor=0`
  para sobrecarregar o sistema (ataque de negação de serviço por esgotamento de recursos)
- Viola a semântica contábil: uma transferência é, por definição, um movimento financeiro

### 2. Entrada discriminante

| Campo | Valor |
|---|---|
| Endpoint | `POST /transferencia` |
| origem | `1` (Alice — qualquer conta com saldo ≥ 0) |
| destino | `2` (Bob) |
| valor | `0.00` |

Condição exata: **valor igual a zero** (não negativo, não nulo — exatamente `0.0`).

### 3. Resposta esperada

| Sistema | HTTP | Body |
|---|---|---|
| **Original (correto)** | `422` | `{"erro": "Valor deve ser positivo"}` |
| **Mutante (com bug)** | `200 OK` | `{"mensagem": "Transferencia realizada", "valor": 0.0}` |

**Impacto real:** O extrato bancário do cliente passaria a mostrar transferências
de R$ 0,00. Um cliente que consultar seu extrato verá registros como:

```
2026-06-07 18:39  Transferência enviada para Bob       R$    0,00
2026-06-07 18:39  Transferência enviada para Carlos    R$    0,00
```

Além da confusão para o cliente, sistemas de relatório e auditoria que somam
os valores do extrato continuariam funcionando — pois soma(0) = 0 —
mas a **contagem de transações** estaria inflada, podendo acionar alertas
de compliance desnecessariamente.

---

## Quadro comparativo final

| Mutante | Regra de negócio violada | Entrada que ativa | Impacto para o cliente |
|---|---|---|---|
| **M1** (`< → <=`) | Cliente pode usar todo o saldo | `valor == saldo_disponível` | Transferência negada com mensagem falsa de "saldo insuficiente" |
| **M2** (`== → !=`) | Contas distintas podem transferir; mesma conta não | Qualquer `origem != destino` | Todas as transferências bloqueadas; banco inoperante |
| **M3** (`<= 0 → < 0`) | Valor deve ser positivo (> 0, não ≥ 0) | `valor == 0.0` | Extrato poluído com registros fantasmas de R$ 0,00 |
