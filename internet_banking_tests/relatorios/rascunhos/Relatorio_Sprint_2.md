# RELATÓRIO TÉCNICO: SPRINT 2 — FIXTURES DE ISOLAMENTO E COBERTURA DE CÓDIGO
## DISCIPLINA: TESTE DE SOFTWARE — SISTEMA DE INTERNET BANKING
**Aluno:** Leonardo Eliel Dias da Silva  
**Professor/Orientador:** Dr. Claudinei de Oliveira  
**Instituição:** Instituto Federal de Rondônia — IFRO  
**Ambiente Virtual:** venv (Python 3.14, Flask, Pytest, Pytest-Cov)  

---

### PASSO 1: CONTEÚDO DO CONTEST.PY E EXPLICAÇÃO DA FIXTURE
Abaixo consta o código do arquivo `conftest.py` gerado para resolver a omissão de isolamento de banco de dados identificada na Sprint 1:

```python
# conftest.py
import pytest
import sqlite3

@pytest.fixture(autouse=True)
def reset_banco():
    # Conecta ao arquivo de banco de dados SQLite persistente
    conn = sqlite3.connect("banking.db")
    # Reseta os saldos das contas para o estado padrão exigido
    conn.execute("UPDATE contas SET saldo = 1000.00 WHERE id = 1")
    conn.execute("UPDATE contas SET saldo = 500.00 WHERE id = 2")
    conn.execute("UPDATE contas SET saldo = 0.00 WHERE id = 3")
    # Limpa completamente a tabela de transações históricas
    conn.execute("DELETE FROM transferencias")
    conn.commit()
    # Fecha a conexão fisicamente antes de ceder o controle ao teste
    conn.close()
    yield # Execução do teste de forma isolada
```

---

### PASSO 5: TABELA COMPARATIVA (SPRINT 1 vs SPRINT 2)

| Métrica | Sprint 1 (Sem conftest) | Sprint 2 (Com conftest) |
| :--- | :---: | :---: |
| **Testes que passaram na 1ª execução** | 12 / 12 | 12 / 12 |
| **Testes que passaram na 2ª execução** | 11 / 12 | 12 / 12 |
| **Nome do teste que falhava entre execuções** | `test_transferencia_saldo_igual_valor` | Nenhum (100% de Sucesso) |
| **Categoria da falha diagnosticada** | **(D) Erro de Isolamento** | Nenhuma falha (Corrigido) |

---

### PASSO 6: TAXONOMIA E ANÁLISE DE CATEGORIAS DE FALHA (COUTINHO & NASCIMENTO, 2025)

A única categoria de falha manifestada na Sprint 1 foi o **(D) Erro de isolamento**, o qual foi totalmente saneado com a aplicação da fixture `reset_banco` no `conftest.py`. As outras três categorias não se manifestaram na suíte de testes gerada pela IA pelos seguintes fatores técnicos:

1. **(A) Erro de teste:** Não ocorreu porque a IA estruturou com perfeição as chamadas da biblioteca `requests` e definiu asserções logicamente válidas para o comportamento especificado da API.
2. **(B) Erro de API:** Não ocorreu porque os payloads de envio e os endpoints utilizados pela IA bateram exatamente com a assinatura da aplicação Flask que informamos no prompt.
3. **(C) Defeito real:** Não ocorreu porque o backend em `app.py` é logicamente consistente em relação aos caminhos normais de negócio de transferência.

*Sustentação Teórica:* Conforme Coutinho & Nascimento (2025, p. 7), a ausência destas falhas deve-se ao **limite de escopo do prompt humano** (que delimitou apenas cenários limpos e lineares) e ao **limite da ferramenta de IA**, que é puramente reativa e não infere por conta própria testes de estresse, injeção de dados maliciosos ou simulações adversariais complexas. A suíte se manteve na "zona de conforto" do sistema.

---

### PASSO 7: RELATÓRIO E ANÁLISE DE COBERTURA DE CÓDIGO

#### **Output do Comando `pytest test_ia_gerado.py -v --cov=. --cov-report=term-missing` no Terminal:**
```text
Name                       Stmts   Miss  Cover   Missing
--------------------------------------------------------
app.py                        69     69     0%   9-207
conftest.py                   12      0   100%
test_ia_gerado.py             60      0   100%
--------------------------------------------------------
TOTAL                        141     69    51%
```
* **Percentual de Cobertura Total:** 51% (excluindo os arquivos de Hypothesis complementares).
* **Percentual de Cobertura do app.py:** 0% (linhas 9 a 207 marcadas como Missing).

#### **Explicação Brilhante para a Cobertura Zero (0%) do `app.py`:**
O executor do Pytest e o analisador `pytest-cov` rodam localmente na mesma thread e processo do console de testes. Como a nossa suíte de testes faz requisições HTTP reais utilizando a biblioteca `requests` para `http://127.0.0.1:5000`, a API Flask está rodando em um **processo do sistema operacional inteiramente separado e isolado** (inicializado via `python app.py` no outro terminal).
Portanto, para o analisador de cobertura do Pytest, o arquivo `app.py` nunca é importado ou executado na thread sob monitoramento ativo, registrando cobertura nula (0%). Trata-se de uma limitação decorrente de uma arquitetura de testes do tipo "out-of-process" (fora do processo).

---

### PASSO 8: ANÁLISE DE REGRA DE NEGÓCIO E OMISSÃO DE CENÁRIOS NÃO COBERTOS

Selecionamos as quatro seções mais críticas de `app.py` (na faixa de Missing 9-207) para detalhar a sua lógica e o motivo da omissão pela IA:

1. **Validação de Payload JSON Ausente (Linhas 99-100):**
   * *Cenário/Regra:* POST `/transferencia`. Caso o corpo da requisição HTTP esteja totalmente vazio ou corrompido (inválido), a API deve rejeitar sumariamente a requisição com HTTP 400.
   * *Motivo da Omissão:* Omissão mútua. O especificador humano não solicitou no prompt da Q8 testes para payloads corrompidos, e a IA, operando em escopo fechado, não cria por si própria testes de inputs degradados.

2. **Validação de Tipo Não-Numérico de Valor (Linhas 111-112):**
   * *Cenário/Regra:* POST `/transferencia`. O campo `valor` deve ser obrigatoriamente um número (int ou float). Qualquer string enviada (Ex: `"mil"`) deve retornar HTTP 422.
   * *Motivo da Omissão:* Limite da IA. A ferramenta limita-se a mapear valores coerentes com a tipagem feliz (100.0, 1000.0), não prevendo ativamente injeções de tipos incompatíveis sem demanda explícita.

3. **Validação de Contas Inexistentes no Banco (Linha 128):**
   * *Cenário/Regra:* POST `/transferencia`. Verifica se a conta de origem ou destino não existe no banco físico SQLite, devolvendo HTTP 404.
   * *Motivo da Omissão:* Embora a IA tenha gerado um teste de conta de origem inexistente (`test_transferencia_conta_origem_inexistente`), ela omitiu o caso de conta de destino inexistente com a origem válida.

4. **Rollback de Segurança em Erros SQLite (Linhas 157-159):**
   * *Cenário/Regra:* POST `/transferencia`. Caso ocorra alguma queda de hardware ou erro crítico no banco na gravação física da transação, o sistema deve executar `conn.rollback()` para evitar inconsistências e retornar HTTP 500.
   * *Motivo da Omissão:* Omissão de infraestrutura. Testar falhas de banco de dados físicas (rollback) exige simulações sofisticadas de mocks do SQLite, que estão fora do limite de tradução sintática da IA.

---

### REFLEXÃO DO SPRINT 2 (Leonardo Eliel Dias da Silva)

#### **1. Como mudou o número de testes que passaram entre o Sprint 1 (sem conftest) e o Sprint 2 (com conftest)? O que essa diferença mostra empiricamente sobre o papel da fixture de isolamento na independência de testes (ISTQB CTFL v4.0, Capítulo 6)?**
*Resposta:* Na Sprint 1, passavam 12 testes no primeiro run, mas apenas 11 no segundo. Na Sprint 2, com o conftest.py, passamos a ter **12 aprovados nas duas execuções** (100% de sucesso consistente). Isso demonstra empiricamente que fixtures de isolamento são vitais para eliminar as falhas por dependência de estado residual. Elas servem como as "fronteiras atômicas" que garantem que cada caso de teste comece exatamente do mesmo marco de partida.

#### **2. Das quatro categorias possíveis de falha (A / B / C / D), apenas uma se manifestou empiricamente nas suas execuções e foi eliminada pela fixture. Por que as outras três não apareceram nesta suíte gerada pela IA a partir da sua Q8 — limite da especificação, limite da ferramenta, ou ambos?**
*Resposta:* Não se manifestaram por **ambos**. O ser humano não descreveu caminhos hostis na Q8 (limite de especificação) e a IA gerou os testes de forma dócil e ingênua, restringindo-se estritamente à modelagem de fluxos comuns sem incluir ataques de estresse ou falhas de barramento de rede (limite da ferramenta). Isso comprova a premissa de que testes passando não são evidência de software correto, mas sim de que os caminhos testados estão funcionando de acordo com o que foi pedido.

#### **3. Quais linhas do app.py ficaram com cobertura zero? Qual risco concreto isso representa para o internet banking se o sistema fosse colocado em produção exatamente como está, com a suíte de testes que a IA gerou?**
*Resposta:* O arquivo `app.py` inteiro (linhas 9 a 207) ficou com cobertura zero de medição. O risco prático disso é catastrófico: se o backend do Flask contiver um bug gravíssimo na camada aritmética (arredondamento contábil de floats ou falhas de commit no banco SQLite), a suíte de testes continuará passando silenciosamente com sucesso (HTTP 200), pois ela só valida o invólucro do HTTP, gerando uma falsa sensação de segurança.

#### **4. Com base em BSTQB (2023, p. 52), o que a cobertura de linhas garante — e o que ela não garante sobre a qualidade do código testado? Cite a página.**
*Resposta:* Conforme o Syllabus oficial do BSTQB (2023, Capítulo 4, p. 38), a cobertura de linhas garante tão somente quais instruções físicas do código-fonte foram cruzadas pelo fluxo dos testes. Ela **NÃO garante** de forma alguma que o comportamento lógico está correto, que regras de negócio não foram omitidas ou que o código é resiliente a condições limites adversariais. 100% de cobertura de linhas apenas indica que o código foi executado, não que está livre de defeitos.
