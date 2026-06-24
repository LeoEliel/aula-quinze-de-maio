# PORTFÓLIO UNIFICADO: SPRINTS 1, 2 E 3 — LABORATÓRIO DE TESTE DE SOFTWARE
**Aluno:** Leonardo Eliel Dias da Silva  
**Professor:** Dr. Claudinei de Oliveira  
**Instituição:** Instituto Federal de Rondônia — IFRO  
**Ambiente:** Python (venv), Flask, Pytest, Pytest-Cov e Hypothesis  

---

# PARTE 1: SPRINT 1 — REFATURAÇÃO E INDEPENDÊNCIA DE TESTES

### O Problema Encontrado (Erro de Isolamento)
Na Sprint 1, a suíte de testes gerada pela IA passava de primeira (12/12), mas se rodássemos uma segunda vez seguida, um teste falhava (`test_transferencia_saldo_igual_valor`).
* **Por que isso acontecia?** A nossa API usa um banco de dados real SQLite (`banking.db`). No primeiro teste, o saldo de Alice (R$ 1000) era todo transferido. Quando rodávamos o teste de novo, o saldo dela já estava em R$ 0, fazendo o teste falhar.
* **Classificação do erro:** **(D) Erro de Isolamento**. O teste falhava porque dependia do estado deixado pelo teste anterior.

### Benefícios de Testes Isolados (BSTQB, 2023)
De acordo com o Syllabus do BSTQB (Capítulo 6), isolar os testes traz três grandes vantagens:
1. **Evita falsos resultados:** Um teste não interfere no resultado do outro.
2. **Facilita achar bugs:** Se um teste falhar, sabemos exatamente qual trecho de código deu erro, sem interferência externa.
3. **Liberdade de execução:** Podemos rodar os testes em qualquer ordem ou até mesmo ao mesmo tempo.

### Reflexão Crítica da Sprint 1

#### **1. Antes de ver o código gerado, você esperava que a IA cobrisse tudo o que você especificou na Q8? O que te surpreendeu - para mais ou para menos?**
*Resposta:* Surpreendeu positivamente a facilidade da IA de mapear endpoints e mensagens de erro exatas, mas negativamente sua ingenuidade ao ignorar a persistência física do SQLite, quebrando as execuções seguidas.

#### **2. Qual foi a diferença mais relevante entre o que você descreveu na Q8 e o que a IA produziu? Por que essa diferença importa para um sistema bancário real?**
*Resposta:* A IA não checou se o saldo no banco foi realmente alterado nem limpou o estado. Em produção, isso é perigoso porque a API pode responder "sucesso" enquanto os saldos ficam corrompidos no banco.

#### **3. Com base no que você leu em Coutinho & Nascimento (2025), o comportamento da IA que você observou é esperado ou inesperado? Cite a página.**
*Resposta:* Esperado. Conforme Coutinho & Nascimento (2025, p. 12), a automação exige total controle sobre o estado dos dados de teste. Sem reset e setup adequados, os testes tornam-se frágeis e instáveis.

#### **4. Em uma linha: qual é o limite fundamental da IA nesse tipo de tarefa?**
*Resposta:* A IA é excelente com código e sintaxe local, mas carece de visão sistêmica de infraestrutura física e ciclo de vida do ambiente.

---

# PARTE 2: SPRINT 2 — FIXTURES E COBERTURA DE CÓDIGO

### Como Resolvemos o Problema (`conftest.py`)
Criamos uma regra automatizada (fixture) para limpar e restaurar os saldos do banco de dados antes de cada teste rodar:

```python
# conftest.py
import pytest
import sqlite3

@pytest.fixture(autouse=True)
def reset_banco():
    conn = sqlite3.connect("banking.db")
    # Restaura os saldos iniciais padrão
    conn.execute("UPDATE contas SET saldo = 1000.00 WHERE id = 1")
    conn.execute("UPDATE contas SET saldo = 500.00 WHERE id = 2")
    conn.execute("UPDATE contas SET saldo = 0.00 WHERE id = 3")
    # Limpa o histórico de transferências
    conn.execute("DELETE FROM transferencias")
    conn.commit()
    conn.close()
    yield
```

### Resultados Comparativos (Sprint 1 vs Sprint 2)

| Métrica | Sprint 1 (Sem conftest) | Sprint 2 (Com conftest) |
| :--- | :---: | :---: |
| **Passou de primeira?** | Sim (12/12) | Sim (12/12) |
| **Passou de segunda?** | Não (11/12) | Sim (12/12) |
| **Teste que falhava** | `test_transferencia_saldo_igual_valor` | Nenhum (Todos passaram sempre!) |
| **Categoria do Erro** | **(D) Erro de Isolamento** | Corrigido |

### Relatório de Cobertura de Código (`pytest-cov`)
Rodamos o comando `pytest test_ia_gerado.py -v --cov=. --cov-report=term-missing` e o resultado foi:

```text
Name                       Stmts   Miss  Cover   Missing
--------------------------------------------------------
app.py                        69     69     0%   9-207
conftest.py                   12      0   100%
test_ia_gerado.py             60      0   100%
--------------------------------------------------------
TOTAL                        141     69    51%
```

* **Por que a cobertura do `app.py` deu 0%?**
  Isso acontece porque o servidor Flask (`app.py`) roda em um terminal separado (outro processo do computador). Os nossos testes fazem chamadas HTTP via internet/rede (`requests`). Para o Pytest local, o arquivo `app.py` nunca foi aberto diretamente dentro da sua execução de testes, marcando 0% de cobertura.

* **Omissões importantes no código que os testes da IA não cobriram:**
  1. *Payloads vazios (Linhas 99-100):* Não havia testes enviando requisições sem dados.
  2. *Valores que não são números (Linhas 111-112):* Não testava o envio de strings no campo de valor (ex: `"cinquenta"`).
  3. *Falhas no banco (Linhas 157-159):* Não testava o comportamento caso o banco SQLite ficasse indisponível ou caísse no meio de uma transação.

### Reflexão Crítica da Sprint 2

#### **1. Como mudou o número de testes que passaram entre o Sprint 1 (sem conftest) e o Sprint 2 (com conftest)? O que essa diferença mostra na prática sobre a independência de testes (ISTQB CTFL v4.0, Capítulo 6)?**
*Resposta:* Sem conftest passavam 11/12 no segundo run; com conftest passam sempre 12/12. Isso prova empiricamente que fixtures de isolamento são indispensáveis para garantir a repetibilidade e a independência de testes exigida pelo ISTQB.

#### **2. Das quatro categorias possíveis de falha (A / B / C / D), apenas o isolamento (D) apareceu. Por que as outras três não apareceram nesta suíte gerada pela IA — limite da especificação, limite da ferramenta, ou ambos?**
*Resposta:* Ambos. O prompt inicial não pediu cenários adversos (especificação) e a IA gerou apenas caminhos felizes óbvios (ferramenta), ocultando possíveis erros de teste, API e defeitos reais.

#### **3. Quais linhas do app.py ficaram com cobertura zero? Qual risco real isso traria se o internet banking fosse para produção desse jeito?**
*Resposta:* O arquivo app.py inteiro ficou com 0% de medição local. O risco real é aprovar e liberar em produção código contendo bugs de cálculo internos simplesmente porque o retorno HTTP deu status 200.

#### **4. Com base no BSTQB (2023, p. 38), o que a cobertura de linhas garante — e o que ela NÃO garante sobre a qualidade do código?**
*Resposta:* Segundo o BSTQB (2023, p. 38), a cobertura garante apenas que uma linha física foi executada, mas não atesta a sua correção lógica, segurança ou ausência de requisitos omitidos.

---

# PARTE 3: SPRINT 3 — TESTES POR PROPRIEDADES (HYPOTHESIS)

### O que são Invariantes?
Em vez de testar valores fixos ("transferir R$ 100"), definimos regras universais que o sistema deve respeitar com qualquer valor gerado aleatoriamente pelo Hypothesis.

1. **Invariante 1:** Transferir valores negativos ou R$ 0,00 deve sempre retornar erro `422`.
2. **Invariante 2:** Consultar saldo de contas que não existem (IDs diferentes de 1, 2 e 3) deve sempre retornar erro `404`.
3. **Invariante 3:** Em qualquer transferência aceita (`200`), a soma dos saldos das duas contas envolvidas após o envio deve ser exatamente a mesma de antes.

### Código Completo do `test_hypothesis.py`

```python
# Leonardo Eliel Dias da Silva - Pt-br - UTF-8
# test_hypothesis.py
import requests
import pytest
from hypothesis import given, strategies as st, assume, settings

BASE_URL = "http://127.0.0.1:5000"

@given(
    origem=st.sampled_from([1, 2, 3]),
    destino=st.sampled_from([1, 2, 3]),
    valor=st.floats(max_value=0.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=30)
def test_invariante1_valor_nao_positivo(origem, destino, valor):
    assume(origem != destino)
    response = requests.post(
        f"{BASE_URL}/transferencia",
        json={"origem": origem, "destino": destino, "valor": float(valor)}
    )
    assert response.status_code == 422
    assert response.json()["erro"] == "Valor deve ser positivo"

@given(
    conta_id=st.integers().filter(lambda x: x not in (1, 2, 3))
)
@settings(max_examples=30)
def test_invariante2_conta_inexistente(conta_id):
    response = requests.get(f"{BASE_URL}/saldo/{conta_id}")
    assert response.status_code == 404
    if "application/json" in response.headers.get("Content-Type", ""):
        assert response.json()["erro"] == "Conta nao encontrada"

@given(
    origem=st.sampled_from([1, 2, 3]),
    destino=st.sampled_from([1, 2, 3]),
    valor=st.floats(min_value=0.01, max_value=2000.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=30)
def test_invariante3_conservacao_saldos(origem, destino, valor):
    assume(origem != destino)
    
    resp_origem_antes = requests.get(f"{BASE_URL}/saldo/{origem}")
    resp_destino_antes = requests.get(f"{BASE_URL}/saldo/{destino}")
    assume(resp_origem_antes.status_code == 200)
    assume(resp_destino_antes.status_code == 200)
    
    saldo_origem_antes = resp_origem_antes.json()["saldo"]
    saldo_destino_antes = resp_destino_antes.json()["saldo"]
    
    response = requests.post(
        f"{BASE_URL}/transferencia",
        json={"origem": origem, "destino": destino, "valor": float(valor)}
    )
    
    if response.status_code == 200:
        resp_origem_depois = requests.get(f"{BASE_URL}/saldo/{origem}")
        resp_destino_depois = requests.get(f"{BASE_URL}/saldo/{destino}")
        
        assert resp_origem_depois.status_code == 200
        assert resp_destino_depois.status_code == 200
        
        saldo_origem_depois = resp_origem_depois.json()["saldo"]
        saldo_destino_depois = resp_destino_depois.json()["saldo"]
        
        soma_antes = saldo_origem_antes + saldo_destino_antes
        soma_depois = saldo_origem_depois + saldo_destino_depois
        
        assert abs(soma_antes - soma_depois) < 1e-5
```

### Tabela de Comparação (IA Exemplos vs Hypothesis Propriedades)

| Caso de Teste Crítico | Gerado pela IA (Sprint 1)? | Encontrado pelo Hypothesis (Sprint 3)? | Relevância no Banco |
| :--- | :---: | :---: | :--- |
| **Valor 0.0 rejeitado** | Sim | Sim (Invariante 1) | Evita transações inúteis no histórico do cliente. |
| **Valor -0.001 rejeitado** | Parcial (Testou apenas -50.0) | Sim (Invariante 1) | Previne transferências com valores negativos muito pequenos. |
| **Conta inexistente (9999)** | Parcial (Usou apenas ID 99) | Sim (Invariante 2) | Garante que qualquer conta inválida retorne erro 404 de forma padrão. |
| **Saldo total conservado** | Não (Só testou saldos individuais) | Sim (Invariante 3) | Garante que nenhum dinheiro suma ou seja criado do nada. |
| **Float com muitas casas decimais** | Não (Só usou valores redondos) | Sim (Invariante 3) | Previne erros de arredondamento nos centavos residuais. |

### Reflexão Crítica da Sprint 3

#### **1. O Hypothesis encontrou algum caso que a IA não gerou no Sprint 1? Se sim, qual é a relevância desse caso para um sistema bancário real em produção?**
*Resposta:* Sim. O Hypothesis gerou floats negativos extremamente pequenos (-0.001) e IDs imensos, o que é fundamental em produção para evitar bugs reais de arredondamento e vazamentos de integridade.

#### **2. Qual foi a diferença fundamental entre “gerar exemplos” e “verificar propriedades”? Use suas próprias palavras.**
*Resposta:* Gerar exemplos valida caminhos pontuais específicos e planejados (fotos estáticas). Verificar propriedades testa leis matemáticas gerais sob dados em massa gerados aleatoriamente (filmes dinâmicos).

#### **3. Depois de executar o Hypothesis, você confia mais ou menos nos testes gerados pela IA nos Sprints 1 e 2? Justifique com base no que você observou empiricamente, citando MacIver et al. (2019).**
*Resposta:* Confio menos. Conforme MacIver et al. (2019), testes gerados por IA limitam-se aos caminhos óbvios e previstos, enquanto os testes baseados em propriedades varrem de forma contínua e acham pontos cegos extremos.

#### **4. Existe alguma invariante do internet banking que o Hypothesis não conseguiria verificar automaticamente? Qual e por quê?**
*Resposta:* Sim. Critérios subjetivos como qualidade de design, ergonometria visual e facilidade de navegação (UX) para o usuário, que não possuem regras matemáticas ou asserções exatas.

---

# PARTE 4: ATIVIDADE COMPLEMENTAR (ANÁLISE DE INVARIANTES EXTRAS)

Formulamos e testamos duas regras adicionais inéditas para cobrir outras áreas da API. Abaixo está a análise de cada uma de acordo com o Roteiro da Atividade Complementar (Passo 5):

### 🧪 Invariante Extra 1: Transferência para a mesma conta (Circular)
* **a) Enunciado da Invariante:** Para qualquer conta ID cadastrada no sistema $i \in \{1, 2, 3\}$ e qualquer valor positivo $v$, tentar efetuar uma transferência de si para si mesma deve sempre retornar erro `422`.
* **b) Resultado do Pytest:** **PASSED** (Sem falhas observadas).
* **c) Classificação na Taxonomia:** Não se aplica (teste passou sem falhas).
* **d) Relevância no Domínio Bancário:** Previne recursões inúteis e concorrência no SQLite, além de evitar poluição e lançamento de dados redundantes de extrato.

### 🧪 Invariante Extra 2: Extrato de conta inexistente
* **a) Enunciado da Invariante:** Para qualquer ID de conta inexistente $i \notin \{1, 2, 3\}$, consultar o extrato em `/extrato/<i>` deve retornar sempre `HTTP 404`.
* **b) Resultado do Pytest:** **PASSED** (Sem falhas observadas).
* **c) Classificação na Taxonomia:** Não se aplica (teste passou sem falhas).
* **d) Relevância no Domínio Bancário:** Garante consistência universal nos erros e protege o sistema contra ataques de reconhecimento (enumeração de contas válidas na API).

---

### Código Completo do `test_hypothesis_extra.py`

```python
# Leonardo Eliel Dias da Silva - Pt-br - UTF-8
# test_hypothesis_extra.py
import requests
import pytest
from hypothesis import given, strategies as st, assume, settings

BASE_URL = "http://127.0.0.1:5000"

@given(
    conta_id=st.sampled_from([1, 2, 3]),
    valor=st.floats(min_value=0.01, max_value=1000.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=30)
def test_invariante_extra1_mesma_conta(conta_id, valor):
    response = requests.post(
        f"{BASE_URL}/transferencia",
        json={"origem": conta_id, "destino": conta_id, "valor": float(valor)}
    )
    assert response.status_code == 422
    assert response.json()["erro"] == "Origem e destino nao podem ser iguais"

@given(
    conta_id=st.integers().filter(lambda x: x not in (1, 2, 3))
)
@settings(max_examples=30)
def test_invariante_extra2_extrato_inexistente(conta_id):
    response = requests.get(f"{BASE_URL}/extrato/{conta_id}")
    assert response.status_code == 404
    if "application/json" in response.headers.get("Content-Type", ""):
        assert response.json()["erro"] == "Conta nao encontrada"
```

### Output da Execução no Terminal
```text
test_hypothesis_extra.py::test_invariante_extra1_mesma_conta PASSED      [ 50%]
test_hypothesis_extra.py::test_invariante_extra2_extrato_inexistente PASSED [100%]
============================== 2 passed in 1.41s ===============================
```
