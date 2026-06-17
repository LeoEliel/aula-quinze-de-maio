# features/saldo_extrato.feature
# Sprint 5 — BDD com pytest-bdd
# Leonardo Eliel Dias da Silva

Feature: Consulta de saldo e extrato
  Como cliente do banco
  Quero consultar meu saldo e extrato
  Para acompanhar a movimentacao da minha conta

  Scenario: Consultar saldo de conta existente retorna dados corretos
    Given a conta 1 tem saldo de 1000.00
    When o cliente consulta o saldo da conta 1
    Then a resposta deve ter status 200
    And o campo "conta_id" deve ser 1
    And o campo "titular" deve ser "Alice"
    And o campo "saldo" deve estar presente

  Scenario: Consultar saldo de conta inexistente retorna 404
    Given o sistema esta inicializado
    When o cliente consulta o saldo da conta 999
    Then a resposta deve ter status 404
    And a mensagem de erro deve ser "Conta nao encontrada"

  Scenario: Consultar extrato de conta existente retorna historico
    Given o sistema esta inicializado
    When o cliente consulta o extrato da conta 1
    Then a resposta deve ter status 200
    And o campo "historico" deve estar presente
    And o campo "saldo_atual" deve estar presente

  Scenario: Consultar extrato de conta inexistente retorna 404
    Given o sistema esta inicializado
    When o cliente consulta o extrato da conta 999
    Then a resposta deve ter status 404
    And a mensagem de erro deve ser "Conta nao encontrada"
