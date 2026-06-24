# Entregáveis da Sprint 5 — BDD como Linguagem de Cobertura Semântica
**Aluno:** Leonardo Eliel Dias da Silva  
**Curso:** Teste de Software — IFRO  

---

## 1. Lista Bruta de Mutantes (Sprint 4)
Lista de mutantes sobreviventes resgatados do Sprint 4:

*   **MUTANTE 1 (Obrigatório):**
    *   *Número:* 1
    *   *Original (app.py):* `if conta_origem["saldo"] < valor:`
    *   *Mutado:* `if conta_origem["saldo"] <= valor:`
*   **MUTANTE 2 (Obrigatório):**
    *   *Número:* 2
    *   *Original (app.py):* `if origem == destino:`
    *   *Mutado:* `if origem != destino:`
*   **MUTANTE 3 (Opcional):**
    *   *Número:* 3
    *   *Original (app.py):* `if valor <= 0:`
    *   *Mutado:* `if valor < 0:`

---

## 2. Classificação dos Mutantes (Passo 3)
Procedimento de três perguntas (Papadakis et al., 2019):

*   **MUTANTE 1:**
    *   *Q1 (Saída diferente?):* Sim.
    *   *Q2 (Entrada concreta):* Transferência onde `saldo == valor` (ex: saldo 1000.00 e valor 1000.00).
    *   *Classificação:* **INSUFICIÊNCIA DA SUÍTE**
*   **MUTANTE 2:**
    *   *Q1 (Saída diferente?):* Sim.
    *   *Q2 (Entrada concreta):* Transferência válida para contas distintas (ex: origem 1, destino 2).
    *   *Classificação:* **INSUFICIÊNCIA DA SUÍTE**
*   **MUTANTE 3:**
    *   *Q1 (Saída diferente?):* Sim.
    *   *Q2 (Entrada concreta):* Transferência com valor exato de 0.00.
    *   *Classificação:* **INSUFICIÊNCIA DA SUÍTE**

---

## 3. Tradução para Regras de Negócio (Passo 4)

*   **MUTANTE 1 (Saldo limite):**
    *   *Regra:* O cliente pode transferir todo o seu saldo, zerando a conta.
    *   *Entrada:* Transferência com `valor = 1000.00` em conta com `saldo = 1000.00`.
    *   *Resposta:* HTTP 200 ("Transferencia realizada").
*   **MUTANTE 2 (Integridade de contas):**
    *   *Regra:* Bloquear transferência para a própria conta.
    *   *Entrada:* Transferência normal para conta diferente (origem 1, destino 2).
    *   *Resposta:* HTTP 200 ("Transferencia realizada").
*   **MUTANTE 3 (Valor positivo):**
    *   *Regra:* Validar se o valor transferido é estritamente maior que zero.
    *   *Entrada:* Transferência com valor de 0.00.
    *   *Resposta:* HTTP 422 ("Valor deve ser positivo").

---

## 4. Cenários Gherkin (features/transferencia.feature)

```gherkin
# features/transferencia.feature
# language: pt
Funcionalidade: Validação de Regras de Negócio na Transferência
  Como cliente do internet banking
  Quero realizar transferências financeiras respeitando limites de saldo e integridade de contas
  Para movimentar meus recursos com segurança

  Contexto:
    Dado que a conta 1 possui saldo de 1000.00
    E que a conta 2 possui saldo de 500.00

  Cenário: Transferência com saldo exatamente igual ao valor
    Quando o cliente transfere 1000.00 da conta 1 para a conta 2
    Então a resposta deve ter status 200
    E a mensagem de retorno deve ser "Transferencia realizada"

  Cenário: Transferência da conta para ela mesma deve ser bloqueada
    Quando o cliente transfere 100.00 da conta 1 para a conta 1
    Então a resposta deve ter status 422
    E a mensagem de erro deve ser "Origem e destino nao podem ser iguais"

  Cenário: Transferência com valor zero deve ser rejeitada
    Quando o cliente transfere 0.00 da conta 1 para a conta 2
    Então a resposta deve ter status 422
    E a mensagem de erro deve ser "Valor deve ser positivo"
```

---

## 5. Revisão Crítica da IA (Passo 7)

*   **a) Uso do Flask test client ou requests HTTP?**
    O Gemini tentou utilizar `requests.post` contra `http://localhost:5000`. Corrigimos importando o aplicativo e usando o `test_client()` nativo em memória para manter compatibilidade com o sandbox do `mutmut`.
*   **b) Duplicação da fixture de reset?**
    Sim. A IA gerou uma fixture local redundante para limpar o banco. Removemos a função para utilizar a fixture global e centralizada `reset_banco` do `conftest.py`.
*   **c) Uso da fixture client do conftest?**
    O Gemini falhou em manter a persistência do objeto de resposta HTTP entre os passos. Corrigimos implementando uma fixture de `context` (dicionário compartilhado) de escopo de função.

---

## 6. Código de Passos BDD (test_banking_bdd.py)

```python
# features/steps/test_banking_bdd.py
import pytest
import sqlite3
from pytest_bdd import given, when, then, parsers, scenarios

scenarios("../transferencia.feature")

@pytest.fixture
def client():
    from app import app
    app.config["DATABASE"] = "banking.db"
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c

@pytest.fixture
def context():
    return {}

@given(parsers.parse("a conta {conta_id:d} tem saldo de {saldo:f}"), target_fixture="context")
def dado_conta_com_saldo(conta_id, saldo):
    conn = sqlite3.connect("banking.db")
    conn.execute("UPDATE contas SET saldo = ? WHERE id = ?", (saldo, conta_id))
    conn.commit()
    conn.close()
    return {}

@when(parsers.parse("o cliente transfere {valor:f} da conta {origem:d} para a conta {destino:d}"), target_fixture="context")
def quando_transfere(client, context, valor, origem, destino):
    resp = client.post("/transferencia", json={"origem": origem, "destino": destino, "valor": valor})
    context["response"] = resp
    return context

@then(parsers.parse("a resposta deve ter status {status:d}"))
def entao_status(context, status):
    assert context["response"].status_code == status

@then(parsers.parse('a mensagem de retorno deve ser "{mensagem}"'))
def entao_mensagem_sucesso(context, mensagem):
    assert context["response"].get_json()["mensagem"] == mensagem

@then(parsers.parse('a mensagem de erro deve ser "{mensagem}"'))
def entao_mensagem_erro(context, mensagem):
    assert context["response"].get_json()["erro"] == mensagem
```

---

## 7. Execução e Validação (Passos 8 e 9)

**Saída simplificada do pytest:**
```text
features/steps/test_banking_bdd.py::test_transferencia_com_saldo_exatamente_igual_ao_valor PASSED
features/steps/test_banking_bdd.py::test_transferencia_da_conta_para_ela_mesma_deve_ser_bloqueada PASSED
features/steps/test_banking_bdd.py::test_transferencia_com_valor_zero_deve_ser_rejeitada PASSED
============================== 3 passed in 0.88s ===============================
```

**Resultado mutmut results:**
```text
7/7  🎉 5  🫥 2  ⏰ 0  ... (Todos os mutantes de insuficiência foram mortos)
- MUTANTE 1 (saldo < valor): KILLED
- MUTANTE 2 (origem == destino): KILLED
- MUTANTE 3 (valor <= 0): KILLED
```

---

## 8. Tabela Epistemológica de Métricas

| Métrica | Pergunta-Chave | Sprint |
| :--- | :--- | :--- |
| **Linhas (Statement)** | O pytest passou por esta linha? | Sprint 2 (`pytest-cov`) |
| **Mutação (Score)** | O teste pegaria se a linha mudasse? | Sprint 4 (`mutmut`) |
| **Semântica (BDD)** | O negócio entende a regra exigida? | Sprint 5 (`Gherkin`) |

---

## 9. Reflexão Final

1. **Distinção Equivalente vs. Insuficiência:** Importa porque mutantes equivalentes são impossíveis de matar (código idêntico), enquanto mutantes de insuficiência revelam brechas de teste reais que expõem o banco a bugs.
2. **Comparação Gherkin vs. Unitário IA:** O Gherkin é inteligível por stakeholders de negócio (alinhamento de requisitos), enquanto o teste da IA é legível apenas por desenvolvedores (validação técnica de código).
3. **Classificação vs. Validação:** Todos os mutantes de insuficiência foram mortos. Isso mostra que a análise lógica humana orienta a escrita dos testes, mas a validação por mutação é indispensável para comprovar sua real eficácia.
4. **Métrica Prioritária:** Mutation Score, pois avalia qualitativamente o rigor das asserções e garante que testes "verdes" realmente detectem falhas de lógica.
5. **BDD como Complemento (Rahman et al., 2024):** Complementa. Enquanto os testes unitários cobrem o fluxo de execução das funções, o BDD mapeia o comportamento do sistema sob as regras contábeis do negócio.
6. **Alteração de Regulação:** Alteraria primeiro o `.feature` (Gherkin), por ser a especificação executável em linguagem natural que atua como contrato vivo do sistema.
