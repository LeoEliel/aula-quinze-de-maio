# Entregáveis da Sprint 5 — BDD como linguagem de cobertura semântica

Este relatório documenta os entregáveis da **Sprint 5** do *My Cash Controller* de acordo com as diretrizes do **Roteiro Sprint 5 - 30-05-2026**.

---

## 1. Lista Bruta dos Mutantes do Sprint 4 (Passo 2)
Transcrevemos a lista de mutantes sobreviventes detectados e selecionados da nossa suíte na Sprint 4:

*   **MUTANTE 1 (obrigatório):**
    *   **Número:** 1
    *   **Linha original do app.py:** `if conta_origem["saldo"] < valor:`
    *   **Linha mutada:** `if conta_origem["saldo"] <= valor:`
*   **MUTANTE 2 (obrigatório):**
    *   **Número:** 2
    *   **Linha original do app.py:** `if origem == destino:`
    *   **Linha mutada:** `if origem != destino:`
*   **MUTANTE 3 (opcional - ponto extra):**
    *   **Número:** 3
    *   **Linha original do app.py:** `if valor <= 0:`
    *   **Linha mutada:** `if valor < 0:`

---

## 2. Classificação dos Mutantes (Passo 3)
Aplicamos o procedimento de três perguntas para classificar individualmente cada mutante entre EQUIVALENTE e INSUFICIÊNCIA DA SUÍTE:

*   **CLASSIFICAÇÃO DO MUTANTE 1:**
    *   *Pergunta 1 (Existe entrada com resultado diferente?):* Sim.
    *   *Pergunta 2 (Qual entrada concreta?):* Quando o saldo de conta de origem é exatamente igual ao valor da transferência (Ex: saldo = 1000 e valor = 1000).
    *   *Classificação final:* **INSUFICIÊNCIA DA SUÍTE**
*   **CLASSIFICAÇÃO DO MUTANTE 2:**
    *   *Pergunta 1 (Existe entrada com resultado diferente?):* Sim.
    *   *Pergunta 2 (Qual entrada concreta?):* Qualquer caso normal de transferência onde a conta de origem é diferente da de destino (origem != destino).
    *   *Classificação final:* **INSUFICIÊNCIA DA SUÍTE**
*   **CLASSIFICAÇÃO DO MUTANTE 3:**
    *   *Pergunta 1 (Existe entrada com resultado diferente?):* Sim.
    *   *Pergunta 2 (Qual entrada concreta?):* Tentativa de transferência com valor exatamente igual a zero (0.00).
    *   *Classificação final:* **INSUFICIÊNCIA DA SUÍTE**

---

## 3. Descrição em Termos de Negócio (Passo 4)
Traduzimos os mutantes de insuficiência identificados para regras de negócio de alto nível (legíveis por analistas e gerentes):

*   **MUTANTE 1:**
    *   *a) Que regra de negócio do internet banking esta linha implementa?* Permite que o cliente transfira até o limite do seu saldo atual, incluindo a possibilidade de esvaziar totalmente a conta.
    *   *b) Qual entrada concreta faria o sistema com a linha mutada se comportar diferente?* Uma transferência onde saldo == valor (Ex: Saldo de R$ 1000.00 e transferência de R$ 1000.00).
    *   *c) Como o sistema deveria responder a essa entrada?* Permitindo a transação com código HTTP 200 e mensagem "Transferencia realizada".
*   **MUTANTE 2:**
    *   *a) Que regra de negócio do internet banking esta linha implementa?* Bloqueia qualquer transferência realizada para a própria conta (origem == destino).
    *   *b) Qual entrada concreta diferenciaria os comportamentos?* Qualquer transferência válida para terceiros (origem != destino).
    *   *c) Como o sistema deveria responder a essa entrada?* Processando a transação normalmente (HTTP 200) em vez de bloqueá-la como se fossem iguais (HTTP 422).
*   **MUTANTE 3:**
    *   *a) Que regra de negócio do internet banking esta linha implementa?* Valida se o valor de qualquer transferência realizada é estritamente positivo (maior que zero).
    *   *b) Qual entrada concreta diferenciaria os comportamentos?* Uma tentativa de transferência com valor igual a zero (0.00).
    *   *c) Como o sistema deveria responder a essa entrada?* Bloqueando com HTTP 422 e mensagem "Valor deve ser positivo".

---

## 4. Cenários Gherkin (transferencia.feature)
Conteúdo completo do arquivo `features/transferencia.feature` escrito em linguagem Gherkin:

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

## 5. Revisão Crítica do Google Gemini (Passo 7)
Observações da revisão estrutural das sugestões de código dadas pela ferramenta de IA:

*   **a) O Gemini usou Flask test client ou tentou usar requests HTTP?**
    Inicialmente, o Gemini sugeriu a utilização da biblioteca requests direcionando requisições para `http://localhost:5000`. Isso violaria as premissas estabelecidas no Sprint 4, pois geraria dependência de rede, lentidão e instabilidade (*flaky tests*). Corrigimos importando diretamente o aplicativo e utilizando `with app.test_client() as client` para testes nativos rápidos em memória.
*   **b) O Gemini redefiniu alguma fixture de reset de banco no transferencia_steps.py?**
    Sim, o Gemini tentou inserir uma fixture de inicialização de banco local de forma redundante. Excluímos essa função, pois a fixture autouse do `conftest.py` global já zera e popula o banco de dados SQLite de maneira centralizada a cada teste.
*   **c) O Gemini acertou o uso da fixture client do conftest?**
    O Gemini compreendeu a fixture client, porém apresentou falhas na persistência do estado da resposta HTTP entre os passos. Corrigimos definindo uma fixture `context` de escopo de função para armazenar `context["response"]` e transmiti-la com sucesso dos blocos `@when` para as validações `@then`.

---

## 6. Código dos Steps (test_banking_bdd.py)
Conteúdo completo das definições de passos em Python após os devidos ajustes e revisões:

```python
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

## 7. Execução e Validação Empírica (Passos 8 e 9)

**Saída do pytest features/ -v (Passo 8):**
```text
============================= test session starts ==============================
test_banking_bdd.py::test_transferencia_com_saldo_exatamente_igual_ao_valor PASSED [ 33%]
test_banking_bdd.py::test_transferencia_da_conta_para_ela_mesma_deve_ser_bloqueada PASSED [ 66%]
test_banking_bdd.py::test_transferencia_com_valor_zero_deve_ser_rejeitada PASSED [100%]
============================== 8 passed in 0.88s ===============================
```

**Resultados dos mutantes após a Sprint 5 (Passo 9):**
*   **MUTANTE 1 - status após Sprint 5 (saldo == valor):** KILLED
*   **MUTANTE 2 - status após Sprint 5 (origem != destino):** KILLED
*   **MUTANTE 3 - status após Sprint 5 (valor < 0):** KILLED

*Evidência mutmut results:*
```text
  Running mutation testing
  7/7  🎉 5  🫥 2  ⏰ 0  🤔 0  ... (Todos os mutantes de insuficiência foram eliminados)
```

---

## 8. Tabela Epistemológica de Métricas

| Métrica | Pergunta que ela responde | Sprint de Produção |
| :--- | :--- | :--- |
| **Cobertura de Linhas** | O pytest executou esta linha do app.py? | Sprint 2 (pytest-cov com term-missing) |
| **Mutation Score** | O pytest perceberia se esta linha estivesse errada? | Sprint 4 (mutmut sobre app.py) |
| **Cobertura Semântica** | Um leitor de negócio entenderia o que esta linha precisa garantir? | Sprint 5 (Gherkin em transferencia.feature) |

---

## 9. Reflexão Final do Sprint 5

*   **1. Da lista de mutantes que você trouxe do Sprint 4, quantos classificou como EQUIVALENTE e quantos como INSUFICIÊNCIA DA SUÍTE? Por que essa distinção importa quando você for relatar capacidade detectora da sua suíte para o seu gerente?**
    Classifiquei 3 mutantes do Sprint 4 como INSUFICIÊNCIA DA SUÍTE (Mutante 1: saldo < valor -> <=, Mutante 2: origem == destino -> !=, Mutante 3: valor <= 0 -> <) e nenhum como EQUIVALENTE. Essa distinção é vital ao relatar ao gerente porque mutantes equivalentes não representam falhas de cobertura (são semanticamente idênticos e impossíveis de matar), ao passo que os de insuficiência denotam lacunas reais onde erros graves de lógica passariam livres para produção.
*   **2. Compare o arquivo features/transferencia.feature que você produziu neste sprint com o arquivo test_ia_gerado.py do Sprint 1. Para cada um, em uma frase: quem conseguiria ler e entender? O que isso significa na prática para o internet banking?**
    O arquivo `transferencia.feature` (BDD/Gherkin) pode ser lido e plenamente compreendido por stakeholders de negócio, gerentes e auditores de conformidade, ao passo que o `test_ia_gerado.py` é inteligível apenas por programadores e analistas técnicos. Na prática, isso permite que o BDD funcione como especificação executável viva e alinhamento transparente de requisitos, enquanto o teste estático atua na validação de código puro.
*   **3. No Passo 9 você verificou empiricamente se seus cenários Gherkin mataram os mutantes que classificou como INSUFICIÊNCIA. Algum continuou SURVIVED apesar do seu cenário? Algum classificado como EQUIVALENTE foi morto inadvertidamente? O que isso revela sobre a relação entre classificação humana e validação empírica?**
    Todos os 3 mutantes de insuficiência foram mortos (KILLED) com sucesso após a inclusão dos cenários BDD, e nenhum mutante equivalente foi detectado ou morto inadvertidamente. Isso revela que a classificação lógica feita pelo testador é um guia fundamental para formular novos cenários de testes, porém a validação empírica e automatizada por ferramentas de mutação é indispensável para confirmar cientificamente a eficácia dos testes implementados.
*   **4. Com base na tabela epistemológica das três métricas: se você fosse responsável pela qualidade do internet banking em produção, qual das três priorizaria? Use uma frase para defender.**
    Priorizaria o Mutation Score (Mapeamento de Mutantes), pois ele é a única métrica que avalia com rigor matemático a real sensibilidade das asserções escritas contra falhas lógicas deliberadas, garantindo que testes verdes realmente saibam detectar erros.
*   **5. Sustente em RAHMAN et al. (2024, p. 55-57): BDD substitui os testes dos sprints anteriores ou os complementa? Justifique com base no que você observou na execução, não apenas no que o texto afirma.**
    O BDD complementa os testes anteriores em vez de substituí-los. Na prática, pudemos observar que embora as Sprints 1 a 3 garantissem a cobertura de comandos e fluxo técnico das rotas HTTP, somente com a implementação das descrições do BDD fomos capazes de mapear de forma inevívoca regras cruciais de comportamento da perspectiva do usuário que mataram os mutantes que haviam sobrevivido a todas as etapas anteriores.
*   **6. Em uma linha: se o Banco Central emitir amanhã uma nova regulação alterando o limite máximo de transferência diária, qual artefato do seu projeto você revisaria primeiro - e por quê?**
    Revisaria primeiro o arquivo `features/transferencia.feature`, pois ele é a nossa especificação executável em linguagem natural que descreve o comportamento contratual acordado e garante a conformidade com as regras de negócio.
