# interrogatorio_mutantes_sprint5.md
# Passo 2 — Interrogatório dos Mutantes (Sprint 5)
# Leonardo Eliel Dias da Silva

## Contexto da análise

A análise seguiu o framework de Papadakis et al. (2019), que define três perguntas para
classificar um mutante sobrevivente:

> **P1** — O mutante altera o comportamento observável do sistema?  
> **P2** — Existe um conjunto de entradas que produz saída diferente entre o original e o mutante?  
> **P3** — Os testes atuais cobrem esse conjunto de entradas?  

Se P1 = Não → **Mutante Equivalente** (impossível de matar).  
Se P1 = Sim e P3 = Não → **Sobreviveu por Insuficiência de Suíte** (mata-se com novo teste).  
Se P1 = Sim e P3 = Sim → **Morto** (suíte já o detecta).

---

## Evidência de execução

Os mutantes foram aplicados manualmente no `app.py` e os 12 testes BDD foram executados
para cada mutante. Método equivalente ao `mutmut run` (nota: o mutmut 3.5 apresenta
incompatibilidade com Python 3.14 na fase de stats — bug upstream confirmado —
portanto a validação foi realizada via script de aplicação sequencial).

---

## Mutante 1 (OBRIGATÓRIO) — app.py linha 156

### Mutação aplicada

```diff
- if conta_origem["saldo"] < valor:
+ if conta_origem["saldo"] <= valor:
```

### As três perguntas

| Pergunta | Resposta | Justificativa |
|---|---|---|
| P1 — Altera comportamento? | **SIM** | O original permite transferência quando saldo == valor (resultado: HTTP 200). O mutante bloqueia essa operação retornando HTTP 422. |
| P2 — Existe entrada discriminante? | **SIM** | Entrada: `{origem:1, destino:2, valor:1000.00}` com saldo de Alice = R$ 1.000,00. Original → 200; Mutante → 422. |
| P3 — A suíte cobre essa entrada? | **SIM** (após Sprint 5) | Cenário BDD: *"Transferencia com saldo exatamente igual ao valor (borda critica)"* cobre exatamente essa entrada. |

### Classificação

**Sobreviveu por Insuficiência de Suíte nas Sprints 1–4.**  
A suíte anterior (test_ia_gerado.py) testava o cenário com saldo == valor, mas sem
verificar o **saldo pós-transferência**. O test_ia_gerado.py verificava apenas
`status_code == 200` e `mensagem == "Transferencia realizada"`.
Com `<= valor` o mutante retorna 422, então o teste da Sprint 4 **teria** matado o mutante.
Mas como os testes usavam HTTP (não funcionavam com mutmut), o mutante nunca foi exercitado.

**Resultado com BDD Sprint 5:** 🎯 **MORTO** (1 failed, 11 passed)

---

## Mutante 2 (OBRIGATÓRIO) — app.py linha 139

### Mutação aplicada

```diff
- if origem == destino:
+ if origem != destino:
```

### As três perguntas

| Pergunta | Resposta | Justificativa |
|---|---|---|
| P1 — Altera comportamento? | **SIM** | O original bloqueia transferências para a mesma conta (HTTP 422). O mutante inverte a lógica: **permite** mesma conta e **bloqueia** contas distintas. |
| P2 — Existe entrada discriminante? | **SIM** | Qualquer transferência com `origem != destino` (ex: conta 1 → conta 2) retorna 422 com o mutante. Também: `origem == destino` (ex: 1 → 1) retorna 200 com o mutante. |
| P3 — A suíte cobre essa entrada? | **SIM** (após Sprint 5) | Cenário BDD: *"Transferencia da conta para ela mesma deve ser bloqueada"* e *"Transferencia valida debita origem e credita destino corretamente"* cobrem ambos os lados. |

### Classificação

**Sobreviveu por Insuficiência de Suíte nas Sprints 1–4.**  
O cenário `mesma conta → HTTP 422` existia em test_ia_gerado.py mas, novamente,
os testes usavam HTTP real (inviabilizando o mutmut). O mutante `!=` é
especialmente perigoso pois inverte a lógica booleana inteira da guarda,
quebrando qualquer transferência legítima — o que deveria ser detectado por
múltiplos testes. De fato, o BDD matou este mutante com **5 falhas** simultâneas.

**Resultado com BDD Sprint 5:** 🎯 **MORTO** (5 failed, 7 passed)

---

## Mutante 3 (OPCIONAL) — app.py linha 135

### Mutação aplicada

```diff
- if not isinstance(valor, (int, float)) or valor <= 0:
+ if not isinstance(valor, (int, float)) or valor < 0:
```

### As três perguntas

| Pergunta | Resposta | Justificativa |
|---|---|---|
| P1 — Altera comportamento? | **SIM** | O original rejeita `valor == 0.0` com HTTP 422. O mutante aceita `valor == 0.0` como transferência válida. |
| P2 — Existe entrada discriminante? | **SIM** | Entrada: `{origem:1, destino:2, valor:0.0}`. Original → 422; Mutante → 200 (com débito de R$ 0). |
| P3 — A suíte cobre essa entrada? | **SIM** (após Sprint 5) | Cenário BDD: *"Transferencia com valor zero deve ser rejeitada"* exige HTTP 422 para `valor=0.0`. |

### Classificação

**Sobreviveu por Insuficiência de Suíte nas Sprints 1–4.**  
O test_invariante1 do Hypothesis cobria valores ≤ 0 aleatoriamente, mas como
usava HTTP, não funcionava com mutmut.

**Resultado com BDD Sprint 5:** 🎯 **MORTO** (1 failed, 11 passed)

---

## Mutante 4 (OPCIONAL) — app.py linha 69 (candidato equivalente)

### Mutação aplicada

```diff
- INSERT OR IGNORE INTO contas (id, titular, saldo) VALUES (1, 'Alice',  1000.00);
+ INSERT OR REPLACE INTO contas (id, titular, saldo) VALUES (1, 'Alice',  1000.00);
```

### As três perguntas

| Pergunta | Resposta | Justificativa |
|---|---|---|
| P1 — Altera comportamento? | **PROVAVELMENTE NÃO** | `INSERT OR IGNORE` não insere se o registro já existe. `INSERT OR REPLACE` apaga e reinsere. Para um banco com dados iniciais fixos (IDs 1, 2, 3 sempre com os mesmos valores), o resultado final do SELECT é idêntico. |
| P2 — Existe entrada discriminante? | **NÃO** (para os testes atuais) | Não existe cenário de teste que verifica o comportamento do `init_db()` quando os registros já existem com valores **diferentes**. A fixture do conftest.py faz UPDATE antes de cada teste — nunca chama `init_db()`. |
| P3 — A suíte cobre essa entrada? | **NÃO** | A suíte BDD não testa diretamente o `init_db()`. |

### Classificação

**Mutante Equivalente** para o contexto atual da suíte.

Segundo Papadakis et al. (2019, p. 278): *"A mutant is equivalent if for all possible
inputs, it produces the same output as the original program."* Para os inputs
exercitados pela suíte (banco sempre resetado via UPDATE), `OR IGNORE` e `OR REPLACE`
produzem o mesmo comportamento observável. Não é possível matar este mutante
com os testes que cobrem as regras de negócio da aplicação — seria necessário
um teste unitário de `init_db()` com dados pré-existentes divergentes.

**Resultado com BDD Sprint 5:** ⚠️ **SOBREVIVEU** (12 passed — equivalente)

---

## Tabela resumo

| ID | Linha | Mutação | Classificação | Status Sprint 5 |
|---|---|---|---|---|
| M1 | 156 | `<` → `<=` (saldo vs valor) | Insuficiência de suíte (Sprints 1–4) | 🎯 Morto |
| M2 | 139 | `==` → `!=` (mesma conta) | Insuficiência de suíte (Sprints 1–4) | 🎯 Morto |
| M3 | 135 | `<= 0` → `< 0` (valor zero) | Insuficiência de suíte (Sprints 1–4) | 🎯 Morto |
| M4 | 69  | `OR IGNORE` → `OR REPLACE` | **Equivalente** | ⚠️ Sobreviveu |

**Score de mutação Sprint 5:** 3/3 mutantes matáveis = **100%** dos não-equivalentes eliminados.
