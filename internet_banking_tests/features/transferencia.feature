# language: pt
# features/transferencia.feature
# Sprint 5 — BDD com pytest-bdd
# Leonardo Eliel Dias da Silva

Funcionalidade: Transferência bancária
  Como cliente do banco
  Quero transferir dinheiro entre contas
  Para que o saldo seja atualizado corretamente em ambas as contas

  # -------------------------------------------------------
  # MUTANTE OBRIGATÓRIO 1
  # app.py linha 156: conta_origem["saldo"] < valor
  # Mutante: operador < vira <=
  # Efeito: transferência com saldo IGUAL ao valor passaria
  #         a retornar 422 (Saldo insuficiente) — bug silencioso.
  # -------------------------------------------------------
  Cenário: Transferencia com saldo exatamente igual ao valor (borda critica)
    Dado a conta 1 tem saldo de 1000.00
    Quando o cliente transfere 1000.00 da conta 1 para a conta 2
    Então a resposta deve ter status 200
    E a mensagem de retorno deve ser "Transferencia realizada"
    E o saldo da conta 1 deve ser 0.00
    E o saldo da conta 2 deve ser 1500.00

  # -------------------------------------------------------
  # MUTANTE OBRIGATÓRIO 2
  # app.py linha 139: origem == destino
  # Mutante: operador == vira !=
  # Efeito: transferencia para a PROPRIA conta seria permitida
  #         e bloquearia contas com mesma origem/destino distintos.
  # -------------------------------------------------------
  Cenário: Transferencia da conta para ela mesma deve ser bloqueada
    Dado a conta 1 tem saldo de 1000.00
    Quando o cliente transfere 100.00 da conta 1 para a conta 1
    Então a resposta deve ter status 422
    E a mensagem de erro deve ser "Origem e destino nao podem ser iguais"

  # -------------------------------------------------------
  # MUTANTE OPCIONAL 1
  # app.py linha 135: valor <= 0
  # Mutante: operador <= vira <
  # Efeito: valor zero seria aceito como transferencia valida.
  # -------------------------------------------------------
  Cenário: Transferencia com valor zero deve ser rejeitada
    Dado a conta 1 tem saldo de 1000.00
    Quando o cliente transfere 0.00 da conta 1 para a conta 2
    Então a resposta deve ter status 422
    E a mensagem de erro deve ser "Valor deve ser positivo"

  # -------------------------------------------------------
  # MUTANTE OPCIONAL 2
  # app.py linha 135: valor <= 0 com valor negativo
  # Mutante: not isinstance removido
  # Efeito: valores negativos passariam a ser aceitos.
  # -------------------------------------------------------
  Cenário: Transferencia com valor negativo deve ser rejeitada
    Dado a conta 1 tem saldo de 1000.00
    Quando o cliente transfere -50.00 da conta 1 para a conta 2
    Então a resposta deve ter status 422
    E a mensagem de erro deve ser "Valor deve ser positivo"

  # -------------------------------------------------------
  # CENÁRIO EXTRA — cobre debito e credito nos dois lados
  # -------------------------------------------------------
  Cenário: Transferencia valida debita origem e credita destino corretamente
    Dado a conta 2 tem saldo de 500.00
    E a conta 3 tem saldo de 0.00
    Quando o cliente transfere 200.00 da conta 2 para a conta 3
    Então a resposta deve ter status 200
    E o saldo da conta 2 deve ser 300.00
    E o saldo da conta 3 deve ser 200.00

  Cenário: Transferencia com saldo insuficiente deve ser bloqueada
    Dado a conta 3 tem saldo de 0.00
    Quando o cliente transfere 100.00 da conta 3 para a conta 1
    Então a resposta deve ter status 422
    E a mensagem de erro deve ser "Saldo insuficiente"

  Cenário: Transferencia com conta de origem inexistente retorna 404
    Dado o sistema esta inicializado
    Quando o cliente transfere 100.00 da conta 999 para a conta 1
    Então a resposta deve ter status 404
    E a mensagem de erro deve ser "Conta nao encontrada"

  Cenário: Transferencia sem campos obrigatorios retorna 400
    Dado o sistema esta inicializado
    Quando o cliente envia uma transferencia sem o campo valor
    Então a resposta deve ter status 400
    E a mensagem de erro deve ser "Campos obrigatorios ausentes: origem, destino, valor"
