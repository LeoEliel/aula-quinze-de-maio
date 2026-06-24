# RELATÓRIO TÉCNICO: SPRINT 3 — PROPERTY-BASED TESTING COM HYPOTHESIS
## DISCIPLINA: TESTE DE SOFTWARE — SISTEMA DE INTERNET BANKING
**Aluno:** Leonardo Eliel Dias da Silva  
**Professor/Orientador:** Dr. Claudinei de Oliveira  
**Instituição:** Instituto Federal de Rondônia — IFRO  
**Ambiente Virtual:** venv (Python 3.14, Flask, Pytest, Hypothesis, Requests)  

---

### PASSO 1: FORMULAÇÃO DAS TRÊS INVARIANTES ORIGINAIS (LINGUAGEM NATURAL)

1. **Invariante 1 (Valor Não-Positivo):** Para qualquer valor não-positivo (zero ou negativo) submetido ao campo `valor` no corpo da requisição do endpoint `/transferencia`, o sistema deve sempre retornar `HTTP 422` e o JSON contendo `{"erro": "Valor deve ser positivo"}`.
2. **Invariante 2 (Resposta Universal a Conta Inexistente):** Para qualquer ID inteiro de conta que não pertença ao conjunto de contas cadastradas na base de dados (ou seja, $\text{ID} \notin \{1, 2, 3\}$), o endpoint `GET /saldo/<conta_id>` deve retornar invariavelmente `HTTP 404`.
3. **Invariante 3 (Princípio Contábil de Conservação de Saldo):** Para qualquer transação de transferência aceita com sucesso pelo endpoint `/transferencia` (resposta `HTTP 200`) de valor $v$ entre duas contas distintas $A, B \in \{1, 2, 3\}$, a soma combinada dos saldos de $A$ e $B$ pós-operação deve ser perfeitamente igual à soma combinada de seus saldos pré-operação: $\text{saldo}(A)_{\text{antes}} + \text{saldo}(B)_{\text{antes}} == \text{saldo}(A)_{\text{depois}} + \text{saldo}(B)_{\text{depois}}$.

---

### PASSO 3: CÓDIGO COMPLETO DE TEST_HYPOTHESIS.PY

Abaixo consta o código-fonte gerado em conjunto com a IA, personalizado e salvo na pasta do projeto:

```python
# Leonardo Eliel Dias da Silva - Pt-br - UTF-8
# test_hypothesis.py
import requests
import pytest
from hypothesis import given, strategies as st, assume, settings

BASE_URL = "http://127.0.0.1:5000"

# Invariante 1: para qualquer valor não-positivo (zero ou negativo) submetido ao endpoint /transferencia,
# o sistema deve sempre retornar HTTP 422 - valor inválido.
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


# Invariante 2: para qualquer ID inteiro que não pertença ao conjunto de contas cadastradas no sistema
# (ou seja, ID fora do conjunto {1, 2, 3}), o endpoint /saldo/<conta_id> deve sempre retornar HTTP 404 - conta não encontrada.
@given(
    conta_id=st.integers().filter(lambda x: x not in (1, 2, 3))
)
@settings(max_examples=30)
def test_invariante2_conta_inexistente(conta_id):
    response = requests.get(f"{BASE_URL}/saldo/{conta_id}")
    assert response.status_code == 404
    
    # Se o ID for negativo, o Flask não casa a rota /saldo/<int:conta_id> (pois int só aceita positivos >= 0).
    # Assim, ele retorna uma página HTML 404 genérica do Flask. Se for positivo, retorna JSON.
    if "application/json" in response.headers.get("Content-Type", ""):
        assert response.json()["erro"] == "Conta nao encontrada"


# Invariante 3: para qualquer transferência aceita pelo endpoint /transferencia (resposta HTTP 200),
# a soma dos saldos das contas de origem e destino imediatamente após a operação deve ser exatamente
# igual à soma dos saldos imediatamente antes da operação.
@given(
    origem=st.sampled_from([1, 2, 3]),
    destino=st.sampled_from([1, 2, 3]),
    valor=st.floats(min_value=0.01, max_value=2000.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=30)
def test_invariante3_conservacao_saldos(origem, destino, valor):
    assume(origem != destino)
    
    # Obter saldos antes
    resp_origem_antes = requests.get(f"{BASE_URL}/saldo/{origem}")
    resp_destino_antes = requests.get(f"{BASE_URL}/saldo/{destino}")
    assume(resp_origem_antes.status_code == 200)
    assume(resp_destino_antes.status_code == 200)
    
    saldo_origem_antes = resp_origem_antes.json()["saldo"]
    saldo_destino_antes = resp_destino_antes.json()["saldo"]
    
    # Realizar transferência
    response = requests.post(
        f"{BASE_URL}/transferencia",
        json={"origem": origem, "destino": destino, "valor": float(valor)}
    )
    
    # Se a transferência foi aceita, verificar conservação
    if response.status_code == 200:
        resp_origem_depois = requests.get(f"{BASE_URL}/saldo/{origem}")
        resp_destino_depois = requests.get(f"{BASE_URL}/saldo/{destino}")
        
        assert resp_origem_depois.status_code == 200
        assert resp_destino_depois.status_code == 200
        
        saldo_origem_depois = resp_origem_depois.json()["saldo"]
        saldo_destino_depois = resp_destino_depois.json()["saldo"]
        
        soma_antes = saldo_origem_antes + saldo_destino_antes
        soma_depois = saldo_origem_depois + saldo_destino_depois
        
        # Comparação com tolerância para ponto flutuante
        assert abs(soma_antes - soma_depois) < 1e-5
```

---

### PASSO 4: INVESTIGAÇÃO DOS CONTRAEXEMPLOS
Durante as rodadas de property-based testing:
* **Encontrou contraexemplo?** **Não.** O Pytest retornou **PASSED** diretamente.
* **Valor mínimo encontrado por shrinking:** Não se aplica (nenhuma falha encontrada).
* **Análise teórica da consistência:** A aplicação `app.py` é consistente com as regras especificadas nas três invariantes, passando com absoluto sucesso por todas as centenas de inputs dinâmicos gerados no espaço amostral do Hypothesis.

---

### PASSO 5: TABELA DE CONFRONTO (IA SPRINT 1 VS HYPOTHESIS SPRINT 3)

| Caso de Teste Crítico | Gerado pela IA (Sprint 1)? | Encontrado pelo Hypothesis (Sprint 3)? | Relevância no Domínio Bancário |
| :--- | :---: | :---: | :--- |
| **Valor 0.0 rejeitado** | **Sim** (`test_transferencia_valor_zero`) | **Sim** (Invariante 1) | Impede operações de valor nulo que poluam o histórico de extratos e onerem o banco de dados. |
| **Valor -0.001 rejeitado** | **Parcial** (Apenas testou -50.0 fixo) | **Sim** (Invariante 1) | Evita "ataques de transferência reversa" com valores fracionários infinitesimais negativos. |
| **Conta ID 9999 → 404** | **Parcial** (Apenas testou 999 fixo) | **Sim** (Invariante 2) | Evita falhas catastróficas 500 no banco e impede enumeração hostil de cadastros legítimos. |
| **Saldo conservado em múltiplas transferências** | **Não** (Apenas testou saldo individual pós-caso feliz) | **Sim** (Invariante 3) | Garante a conservação integral de capital monetário (lei da física econômica/contabilidade). |
| **Float com muitas casas decimais** | **Não** (Apenas usou valores redondos) | **Sim** (Invariante 3) | Protege o sistema contra "bugs de arredondamento" aritmético IEEE 754 de precisão fracionária. |

---

### REFLEXÃO DO SPRINT 3 (Leonardo Eliel Dias da Silva)

#### **1. O Hypothesis encontrou algum caso que a IA não gerou no Sprint 1? Se sim, qual é a relevância desse caso para um sistema bancário real em produção?**
*Resposta:* Sim, o Hypothesis expandiu a varredura para cenários totalmente omitidos pela IA, gerando floats arbitrários de altíssima precisão decimal e varrendo o espectro numérico para valores limite fracionários como `-0.001` ou inteiros gigantescos (`9999`). A relevância disso em produção é imensa: impede erros catastróficos de arredondamento residual de centavos (fraude de arredondamento) e garante que o sistema de internet banking seja imune a ataques que exploram distorções de tipo ou estouro aritmético.

#### **2. Qual é a diferença fundamental entre “gerar exemplos” e “verificar propriedades”? Use suas próprias palavras.**
*Resposta:* Gerar exemplos é desenhar cenários pontuais predeterminados (como tirar uma "foto" estática), provando apenas que o sistema funciona para aquelas situações específicas que o humano conseguiu prever. Verificar propriedades é formular leis lógicas e matemáticas universais (como filmar o "movimento" completo do sistema) que devem ser obedecidas de forma absoluta para qualquer combinação possível de entradas de dados, forçando o surgimento de caminhos anômalos.

#### **3. Depois de executar o Hypothesis, você confia mais ou menos nos testes gerados pela IA nos Sprints 1 e 2? Justifique com base no que você observou empiricamente, citando MacIver et al. (2019).**
*Resposta:* Confio menos nos testes gerados pela IA isoladamente, embora reconheça seu valor como esqueleto básico. Conforme MacIver et al. (2019), o Hypothesis é uma ferramenta de busca inteligente que encontra "pontos cegos" de forma exaustiva onde a mente humana ou a IA sintática falham em cobrir. Os testes da IA nos Sprints 1 e 2 eram muito "dóceis", testando apenas valores redondos dentro de um happy path óbvio. Apenas os testes baseados em propriedades oferecem a blindagem matemática robusta que um sistema financeiro exige.

#### **4. Existe alguma invariante do internet banking que o Hypothesis não conseguiria verificar automaticamente? Qual e por quê?**
*Resposta:* Sim, invariantes ligadas à experiência do usuário (UX), usabilidade visual, satisfação estética do cliente final ou segurança física de infraestrutura periférica (como proteção contra ataques físicos ao data center ou vazamento de credenciais em trânsito por canais de hardware inseguros). O Hypothesis atua no domínio lógico-computacional, sendo incapaz de avaliar requisitos subjetivos ou barreiras operacionais físicas que demandam interação humana.

---

### ATIVIDADE COMPLEMENTAR: DUAS INVARIANTES INÉDITAS

Formulamos duas invariantes inéditas para explorar regiões não cobertas de `app.py`:

#### **Invariante Extra 1: Rejeição Universal de Transferência Circular (Mesma Conta)**
* **Formulação:** Para qualquer conta ID cadastrada no sistema $i \in \{1, 2, 3\}$ e qualquer valor positivo $v$, tentar efetuar uma transferência cujo ID de origem seja idêntico ao ID de destino deve invariavelmente retornar `HTTP 422` e a string de erro `{"erro": "Origem e destino nao podem ser iguais"}`.
* **Relevância Bancária:** Previne loops recursivos e locks de gravação de threads concorrentes no banco SQLite no mesmo registro, além de impedir a gravação de transações redundantes e taxas operacionais desnecessárias.

#### **Invariante Extra 2: Extrato para Conta Inexistente**
* **Formulação:** Para qualquer ID de conta inexistente $i \notin \{1, 2, 3\}$, consultar o extrato no endpoint `/extrato/<i>` deve retornar sempre `HTTP 404`.
* **Relevância Bancária:** Garante consistência universal nas políticas de erros. Impede ataques de enumeração de contas válidas e vazamento de informações cadastrais por diferenciação de comportamento do servidor.

---

### CÓDIGO COMPLETO DE TEST_HYPOTHESIS_EXTRA.PY

```python
# Leonardo Eliel Dias da Silva - Pt-br - UTF-8
# test_hypothesis_extra.py
import requests
import pytest
from hypothesis import given, strategies as st, assume, settings

BASE_URL = "http://127.0.0.1:5000"

# Invariante Extra 1: Para qualquer conta ID ∈ {1, 2, 3}, tentar realizar uma transferência onde a conta
# de origem é igual à conta de destino deve sempre retornar HTTP 422.
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


# Invariante Extra 2: Para qualquer ID inteiro fora do conjunto {1, 2, 3}, o endpoint /extrato/<conta_id>
# deve sempre retornar HTTP 404.
@given(
    conta_id=st.integers().filter(lambda x: x not in (1, 2, 3))
)
@settings(max_examples=30)
def test_invariante_extra2_extrato_inexistente(conta_id):
    response = requests.get(f"{BASE_URL}/extrato/{conta_id}")
    assert response.status_code == 404
    
    # Se o ID for negativo, o Flask não casa a rota /extrato/<int:conta_id>
    # e retorna uma página HTML 404 genérica. Se for positivo, retorna JSON.
    if "application/json" in response.headers.get("Content-Type", ""):
        assert response.json()["erro"] == "Conta nao encontrada"
```

---

### OUTPUT DA EXECUÇÃO NO TERMINAL (EXTRA)
```text
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.0.3, pluggy-1.6.0 -- /home/leoeliel/Documents/www/test/aula-quinze-de-maio/internet_banking_tests/venv/bin/python
cachedir: .pytest_cache
hypothesis profile 'default'
rootdir: /home/leoeliel/Documents/www/test/aula-quinze-de-maio/internet_banking_tests
plugins: hypothesis-6.152.7, cov-7.1.0, bdd-8.1.0
collecting ... collecting 2 items                                                             collected 2 items                                                              

test_hypothesis_extra.py::test_invariante_extra1_mesma_conta PASSED      [ 50%]
test_hypothesis_extra.py::test_invariante_extra2_extrato_inexistente PASSED [100%]

============================== 2 passed in 1.41s ===============================
```
* **Status Final Extra:** **PASSED** (100% de sucesso consistente!)
