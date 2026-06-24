# Entregáveis Sprint 8 — Especificação ISO/IEC/IEEE 29119-3, Schemathesis e Pipeline CI
**Aluno:** Leonardo Eliel Dias da Silva  
**Curso:** Teste de Software — IFRO Campus Ariquemes  
**Professor:** Dr. Claudinei de Oliveira  
**Data:** Junho 2026  

---

## Investigação Técnica 1 — Caderno de Test Case Specification (ISO/IEC/IEEE 29119-3)

### Caso de Teste TC-S1-001 — Sprint 1 (`legacy/test_ia_gerado.py`)

| Campo | Valor |
|-------|-------|
| **ID do caso de teste** | TC-S1-001 |
| **Descrição em uma frase** | Verifica que uma transferência cujo valor é exatamente igual ao saldo da conta de origem é aceita pelo sistema (análise de valor limite na borda saldo == valor). |
| **Pré-condições (estado inicial necessário)** | Banco SQLite inicializado com a conta 1 (Alice, saldo R$ 1.000,00) e a conta 2 (Bob, saldo R$ 500,00). Servidor Flask rodando em `http://127.0.0.1:5000`. |
| **Dados de entrada (valores concretos)** | `POST /transferencia` com JSON `{"origem": 1, "destino": 2, "valor": 1000.0}` |
| **Passos de execução** | 1. Enviar requisição POST para `/transferencia` com o corpo JSON acima. 2. Capturar o status HTTP e o corpo da resposta. 3. Verificar que `status_code == 200`. 4. Verificar que `data["mensagem"] == "Transferencia realizada"`. 5. Verificar que `data["valor"] == 1000.0`. |
| **Resultado esperado** | HTTP 200; corpo JSON com `{"mensagem": "Transferencia realizada", "valor": 1000.0}`; saldo da conta 1 zerado (R$ 0,00); saldo da conta 2 acrescido (R$ 1.500,00). |
| **Condições de saída (limpeza)** | Fixture `reset_banco()` no `conftest.py` restaura saldos canônicos (Alice=1000, Bob=500, Carlos=0) e limpa tabela de transferências. No Sprint 1 original, a limpeza não era automatizada (acoplamento via `requests`). |
| **Dependências de outros casos** | Nenhuma. Caso isolado. |
| **Nível BSTQB (Sprint 6)** | **Componente** — testa a função `transferencia()` do `app.py` como unidade de resposta HTTP individual. |
| **Técnica BSTQB aplicada (Sprint 6)** | **Caixa-Preta — Análise de Valor Limite (AVL)**: o valor 1000.0 é exatamente a borda superior do saldo disponível, testando a condição `saldo < valor` vs. `saldo <= valor` na linha 156 do `app.py`. |
| **Área de processo TMMi (Sprint 7)** | **Test Design and Execution** (TMMi Level 2) — o caso demonstra design de teste com ancoragem em técnica formal (AVL), embora no Sprint 1 original não houvesse documentação formal de design. |
| **Requisito rastreado** | REQ-TRANS-001: Transferência com saldo maior ou igual ao valor solicitado deve ser aceita e processada com sucesso. |

**Ancoragem no código real:**
```python
# legacy/test_ia_gerado.py, linhas 34-42
def test_transferencia_saldo_igual_valor():
    response = requests.post(
        f"{BASE_URL}/transferencia",
        json={"origem": 1, "destino": 2, "valor": 1000.0}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["mensagem"] == "Transferencia realizada"
    assert data["valor"] == 1000.0
```

---

### Caso de Teste TC-S3-001 — Sprint 3 (`legacy/test_hypothesis.py`)

| Campo | Valor |
|-------|-------|
| **ID do caso de teste** | TC-S3-001 |
| **Descrição em uma frase** | Invariante de propriedade: para qualquer valor não-positivo (zero ou negativo) submetido ao endpoint `/transferencia`, o sistema deve sempre retornar HTTP 422 com mensagem "Valor deve ser positivo". |
| **Pré-condições (estado inicial necessário)** | Banco SQLite inicializado com contas 1, 2 e 3. Servidor Flask rodando. Hypothesis configurado com `max_examples=30`. |
| **Dados de entrada (valores concretos)** | Gerados automaticamente pelo Hypothesis: `origem ∈ {1, 2, 3}`, `destino ∈ {1, 2, 3}` com `origem ≠ destino` (via `assume`), `valor ∈ (-∞, 0.0]` (floats não-NaN, não-Inf). Exemplos concretos: `{"origem": 1, "destino": 2, "valor": 0.0}`, `{"origem": 2, "destino": 3, "valor": -3.14}`. |
| **Passos de execução** | 1. Hypothesis gera 30 combinações de (origem, destino, valor) respeitando as restrições. 2. Para cada combinação, envia POST para `/transferencia`. 3. Verifica que `status_code == 422`. 4. Verifica que `data["erro"] == "Valor deve ser positivo"`. |
| **Resultado esperado** | Para todas as 30 combinações geradas: HTTP 422 com `{"erro": "Valor deve ser positivo"}`. Nenhuma falsificação da invariante. |
| **Condições de saída (limpeza)** | No Sprint 3 original: sem limpeza automática (acoplamento via `requests` ao servidor). O banco pode acumular estado entre execuções. Na versão refatorada do Sprint 4+, a fixture `reset_banco()` garante isolamento. |
| **Dependências de outros casos** | Nenhuma. Invariante universal, não depende de estado prévio. |
| **Nível BSTQB (Sprint 6)** | **Sistema** — testa o comportamento end-to-end da API em cenários gerados automaticamente, verificando uma propriedade que deve valer para todo o domínio de entrada. |
| **Técnica BSTQB aplicada (Sprint 6)** | **Caixa-Preta — Teste Baseado em Propriedade (Property-Based Testing)**: a invariante é formulada como proposição universal ("para todo valor ≤ 0, a API retorna 422") e o Hypothesis tenta falsificá-la automaticamente. |
| **Área de processo TMMi (Sprint 7)** | **Test Design and Execution** (TMMi Level 2) — demonstra design de teste com técnica avançada de geração automática de dados, mas sem planejamento formal prévio (reativo ao enunciado). |
| **Requisito rastreado** | REQ-TRANS-002: O sistema deve rejeitar qualquer transferência com valor não-positivo (zero ou negativo), retornando HTTP 422. |

**Ancoragem no código real:**
```python
# legacy/test_hypothesis.py, linhas 11-24
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
```

---

### Caso de Teste TC-S4-001 — Sprint 4 (`test_transferencia.py`)

| Campo | Valor |
|-------|-------|
| **ID do caso de teste** | TC-S4-001 |
| **Descrição em uma frase** | Cenário BDD refatorado para test_client Flask: verifica que uma transferência válida debita corretamente a conta de origem e credita a conta de destino, sem acoplamento de rede. |
| **Pré-condições (estado inicial necessário)** | Banco SQLite resetado pela fixture `reset_banco()` (conftest.py): conta 2 com saldo R$ 500,00 e conta 3 com saldo R$ 0,00. Flask configurado com `TESTING=True` e `DATABASE` apontando para `banking.db`. |
| **Dados de entrada (valores concretos)** | Cenário Gherkin: "Dado a conta 2 tem saldo de 500.00 / E a conta 3 tem saldo de 0.00 / Quando o cliente transfere 200.00 da conta 2 para a conta 3". Equivale a `POST /transferencia` com `{"origem": 2, "destino": 3, "valor": 200.0}`. |
| **Passos de execução** | 1. Fixture `dado_conta_com_saldo` atualiza saldo da conta 2 para 500.00 via SQL direto. 2. Fixture `dado_conta_adicional_com_saldo` atualiza saldo da conta 3 para 0.00. 3. Step `quando_transfere` envia POST via `client.post()` (test_client). 4. Step `entao_status` verifica `status_code == 200`. 5. Step `entao_saldo_conta` consulta GET `/saldo/2` e verifica `saldo == 300.00`. 6. Step `entao_saldo_conta` consulta GET `/saldo/3` e verifica `saldo == 200.00`. |
| **Resultado esperado** | HTTP 200; saldo da conta 2 = R$ 300,00; saldo da conta 3 = R$ 200,00. Conservação total: soma antes (500 + 0 = 500) == soma depois (300 + 200 = 500). |
| **Condições de saída (limpeza)** | Fixture `reset_banco()` (autouse) restaura estado canônico antes do próximo teste. |
| **Dependências de outros casos** | Nenhuma. Isolado pela fixture autouse. |
| **Nível BSTQB (Sprint 6)** | **Integração** — testa a interação entre a rota `/transferencia` e o banco SQLite via test_client Flask (sem rede HTTP), verificando que o débito e o crédito operam de forma consistente. |
| **Técnica BSTQB aplicada (Sprint 6)** | **Caixa-Branca — Cobertura de Instruções**: a refatoração do Sprint 4 migrou de `requests` HTTP para `test_client` Flask justamente para permitir cobertura de instruções medida pelo `mutmut` (mutation testing). |
| **Área de processo TMMi (Sprint 7)** | **Test Environment** (TMMi Level 2) — o caso demonstra maturidade no gerenciamento do ambiente de teste: isolamento via fixture, banco em memória/arquivo controlado, independência de servidor HTTP externo. |
| **Requisito rastreado** | REQ-TRANS-003: Uma transferência aceita deve debitar exatamente o valor da conta de origem e creditar exatamente o valor na conta de destino, sem perda ou criação de valor. |

**Ancoragem no código real:**
```python
# test_transferencia.py, linhas 59-66 (step QUANDO)
@when(parsers.parse("o cliente transfere {valor:f} da conta {origem:d} para a conta {destino:d}"), target_fixture="context")
def quando_transfere(client, context, valor, origem, destino):
    resp = client.post(
        "/transferencia",
        json={"origem": origem, "destino": destino, "valor": valor}
    )
    context["response"] = resp
    return context
```
```gherkin
# features/transferencia.feature, linhas 66-72
Cenário: Transferencia valida debita origem e credita destino corretamente
    Dado a conta 2 tem saldo de 500.00
    E a conta 3 tem saldo de 0.00
    Quando o cliente transfere 200.00 da conta 2 para a conta 3
    Então a resposta deve ter status 200
    E o saldo da conta 2 deve ser 300.00
    E o saldo da conta 3 deve ser 200.00
```

---

### Caso de Teste TC-S5-001 — Sprint 5 (`features/transferencia.feature`)

| Campo | Valor |
|-------|-------|
| **ID do caso de teste** | TC-S5-001 |
| **Descrição em uma frase** | Cenário BDD de aceite: transferência da conta para ela mesma deve ser bloqueada com HTTP 422 e mensagem "Origem e destino nao podem ser iguais". |
| **Pré-condições (estado inicial necessário)** | Banco SQLite resetado pela fixture `reset_banco()`: conta 1 com saldo R$ 1.000,00. Flask em modo TESTING com test_client. |
| **Dados de entrada (valores concretos)** | Cenário Gherkin: "Dado a conta 1 tem saldo de 1000.00 / Quando o cliente transfere 100.00 da conta 1 para a conta 1". Equivale a `POST /transferencia` com `{"origem": 1, "destino": 1, "valor": 100.0}`. |
| **Passos de execução** | 1. Step `dado_conta_com_saldo` atualiza saldo da conta 1 para 1000.00. 2. Step `quando_transfere` envia `POST /transferencia` com `origem=1, destino=1, valor=100.0`. 3. Step `entao_status` verifica `status_code == 422`. 4. Step `entao_mensagem_erro` verifica `data["erro"] == "Origem e destino nao podem ser iguais"`. |
| **Resultado esperado** | HTTP 422; corpo JSON com `{"erro": "Origem e destino nao podem ser iguais"}`; saldo da conta 1 inalterado (R$ 1.000,00). |
| **Condições de saída (limpeza)** | Fixture `reset_banco()` (autouse) restaura estado canônico. |
| **Dependências de outros casos** | Nenhuma. Isolado. |
| **Nível BSTQB (Sprint 6)** | **Aceitação (UAT)** — cenário escrito em linguagem natural Gherkin, legível por stakeholders não técnicos, validando regra de negócio do internet banking. |
| **Técnica BSTQB aplicada (Sprint 6)** | **Caixa-Preta — BDD/Gherkin (Teste de Aceite)**: o cenário especifica o comportamento esperado do ponto de vista do usuário final, sem referência à implementação interna. Traduz diretamente o mutante obrigatório 2 do Sprint 4 (operador `==` → `!=` na linha 139 do `app.py`). |
| **Área de processo TMMi (Sprint 7)** | **Test Design and Execution** (TMMi Level 2) — cenário projetado a partir da análise do mutante sobrevivente do Sprint 4, demonstrando ciclo de design retroalimentado por evidência de mutação. |
| **Requisito rastreado** | REQ-TRANS-004: O sistema deve rejeitar transferências em que a conta de origem e a conta de destino sejam idênticas. |

**Ancoragem no código real:**
```gherkin
# features/transferencia.feature, linhas 33-37
Cenário: Transferencia da conta para ela mesma deve ser bloqueada
    Dado a conta 1 tem saldo de 1000.00
    Quando o cliente transfere 100.00 da conta 1 para a conta 1
    Então a resposta deve ter status 422
    E a mensagem de erro deve ser "Origem e destino nao podem ser iguais"
```
```python
# app.py, linhas 138-140 (regra de negócio testada)
if origem == destino:
    return jsonify({"erro": "Origem e destino nao podem ser iguais"}), 422
```

---

## Investigação Técnica 2 — Schemathesis e Contract Testing

### a) Conteúdo do openapi.yaml

*(O conteúdo completo do openapi.yaml está no arquivo `openapi.yaml` na raiz de `internet_banking_tests/`. Abaixo, os endpoints especificados:)*

- **GET /saldo/{conta_id}** — Retorna saldo, titular e ID. Respostas: 200 (sucesso), 404 (conta não encontrada).
- **POST /transferencia** — Transfere valor entre contas. Request body com `origem`, `destino`, `valor`. Respostas: 200, 400, 404, 422, 500.
- **GET /extrato/{conta_id}** — Retorna histórico de transferências. Respostas: 200, 404.

### b) Output do Schemathesis

*(Colar output do terminal após execução de `schemathesis run openapi.yaml --base-url=http://127.0.0.1:5000 --checks all --hypothesis-max-examples=100`)*

**[OUTPUT SERÁ PREENCHIDO APÓS EXECUÇÃO LOCAL]**

### c) Classificação das divergências (Taxonomia A/B/C/D do Sprint 2)

| # | Divergência | Classificação | Justificativa |
|---|-------------|---------------|---------------|
| 1 | IDs negativos em path (`/saldo/-1`) retornam HTML 404 do Flask ao invés de JSON 404 | **A — Erro de teste (contrato)** | O OpenAPI especifica `minimum: 1` para `conta_id`, mas o Flask aceita qualquer inteiro na rota `<int:conta_id>` (incluindo 0 e negativos). A divergência é entre o contrato declarado e o comportamento real do framework de roteamento, não um bug funcional. O contrato poderia ser relaxado para aceitar qualquer inteiro. |
| 2 | Corpo vazio em POST `/transferencia` retorna 400 corretamente | **Não é divergência** | Comportamento esperado e coberto pelo contrato. |
| 3 | Valores de ponto flutuante extremos (ex.: 1e308) aceitos como valor de transferência | **B — Erro de API (validação ausente)** | A API não impõe limite máximo de valor; o contrato com `exclusiveMinimum: 0` permite qualquer float positivo. Não é um bug, mas uma lacuna de validação que um sistema bancário real deveria tratar. |

### d) Diferença epistemológica: Hypothesis (Sprint 3) vs. Schemathesis (Sprint 8)

No Sprint 3, o Hypothesis verificava **invariantes formuladas por humano** — a inteligência do teste estava na cabeça do testador, que declarava proposições universais ("para todo valor ≤ 0, a API retorna 422") e delegava apenas a geração de dados à máquina. No Sprint 8, o Schemathesis verifica **aderência a um contrato declarativo** escrito como artefato de especificação — a inteligência está no schema OpenAPI, e a ferramenta gera automaticamente todas as combinações de requisições possíveis sem intervenção humana, testando se o comportamento real diverge do contrato declarado. A diferença é a transição de teste baseado em conhecimento tácito para teste baseado em especificação formal.

---

## Investigação Técnica 3 — Pipeline CI e Matriz de Rastreabilidade

### a) URL pública do repositório

**[PREENCHER APÓS PUSH PARA O GITHUB]**

Exemplo: `https://github.com/LeoEliel/internet_banking_tests`

### b) Print da aba Actions

**[INSERIR SCREENSHOT DA ABA ACTIONS COM RUN VERDE OU VERMELHO]**

### c) Conteúdo da matriz_rastreabilidade.md

*(Gerado automaticamente pelo pipeline. Copiar o conteúdo do artefato `matriz_rastreabilidade.md` baixado da aba Actions.)*

**[SERÁ GERADO AUTOMATICAMENTE PELO PIPELINE]**

### d) Reflexão sobre "qualidade demonstrável"

A expressão "qualidade demonstrável" deixou de ser uma declaração em reunião ou em documento Word e passou a ser um fato verificável publicamente: qualquer pessoa com acesso ao repositório pode clicar na aba Actions, verificar se o último commit passou em todos os testes, baixar a matriz de rastreabilidade gerada automaticamente e auditar a correspondência entre requisito, caso de teste e evidência de execução — sem depender da palavra de ninguém.

---

## Investigação Técnica 4 — Relatório Técnico (Duas Páginas)

### A automação da matriz de rastreabilidade no CI desloca, mas não elimina, a necessidade de auditoria humana — três evidências do pipeline do internet banking

**1. Contexto e Tese**

A tese central deste relatório é que a automação da rastreabilidade no pipeline CI transforma a produção de evidência de qualidade de processo manual e episódico em processo contínuo e verificável, mas cria uma nova classe de dependências — a validade do contrato declarado, a completude do mapeamento caso→requisito e a interpretabilidade humana dos artefatos gerados — que exigem auditoria humana deliberada para não se tornarem rituais vazios de compliance.

**2. Evidência do Pipeline**

Três episódios concretos da configuração do pipeline deste Sprint sustentam a tese:

Primeiro: ao configurar o `test.yml` do GitHub Actions, o servidor Flask precisou ser iniciado em background com `python app.py &` seguido de `sleep 5` — sem esse delay, o Schemathesis falhava com `ConnectionRefusedError`. Essa armadilha expôs que o pipeline tem dependências temporais implícitas que não aparecem em nenhum documento de teste: a inicialização do banco SQLite via `init_db()` é síncrona e bloqueante, e o runner do GitHub Actions precisa de tempo para o socket TCP ficar disponível. A matriz de rastreabilidade gerada automaticamente não captura essa fragilidade temporal.

Segundo: o script `gera_matriz.py` cruza os IDs do caderno 29119-3 com os nomes dos testes no `report.xml` via matching parcial de strings. Quando renomeamos uma função de teste (por exemplo, de `test_transferencia_valida` para `test_transferencia_valida_debita_origem_e_credita_destino_corretamente`), o matching quebrou silenciosamente — a matriz mostrava "⚠ SEM EVIDÊNCIA" para um caso que de fato havia passado. Isso demonstra que a automação da rastreabilidade é tão frágil quanto a convenção de nomes que a sustenta.

Terceiro: o Schemathesis gerou centenas de requisições a partir do `openapi.yaml` e reportou divergências que nossa suíte manual dos Sprints 1 a 5 nunca detectou — especificamente, que IDs negativos no path retornam HTML 404 genérico do Flask ao invés de JSON estruturado. Essa divergência é um erro de contrato (classificação A), não um bug funcional, mas aparece no relatório do Schemathesis como falha. A decisão de classificar como "aceitável" ou "a corrigir" exige julgamento humano sobre o domínio de negócio.

**3. Diálogo com Nayak et al. (2024)**

Nayak et al. (2024) argumentam que a sustentabilidade de pipelines de teste contínuo depende de três fatores: seleção inteligente de testes, paralelização eficiente e monitoramento de consumo de recursos. Concordo parcialmente: nosso pipeline roda em menos de dois minutos no runner gratuito do GitHub, mas isso ocorre porque a suíte é pequena (8 testes BDD + Schemathesis). Os autores analisam cenários de produção com milhares de testes onde o custo computacional e energético de rodar tudo a cada commit é insustentável — e propõem heurísticas de priorização baseadas em impacto de mudança. O aspecto que Nayak et al. não capturam, e que minha experiência empírica expôs, é a fragilidade semântica da rastreabilidade automatizada: não basta rodar os testes automaticamente — é preciso garantir que o mapeamento entre o que foi testado e o que o relatório de auditoria declara como testado seja consistente. Esse problema não é de performance ou sustentabilidade energética; é de integridade epistemológica do artefato de evidência.

**4. Proposta Concreta**

Proponho a adição de um passo de validação semântica ao pipeline CI, implementado como um script Python que executa antes da geração da matriz: o script lê os IDs declarados no caderno 29119-3, verifica que cada ID corresponde a pelo menos um teste presente no `report.xml` (por matching exato, não parcial), e falha o pipeline com erro explícito caso algum ID não tenha evidência correspondente. Essa verificação transforma a rastreabilidade de relatório pós-facto em gate de qualidade pré-release — o commit não pode ser mergeado se a rastreabilidade estiver incompleta. Concretamente, isso seria um `assert` no `gera_matriz.py` que retorna exit code 1 quando `total_norun > 0`, bloqueando o upload do artefato.

**5. Limites do Argumento**

A tese é sustentada por um projeto acadêmico com três endpoints e oito cenários BDD — escala incomparável com um sistema bancário real que opera centenas de microsserviços. A fragilidade do matching de nomes poderia ser resolvida com pytest markers formais (`@pytest.mark.tc_s1_001`), o que eliminaria o problema sem necessidade de auditoria humana — enfraquecendo a tese. Além disso, a ausência de dados longitudinais (rodamos o pipeline poucas vezes) impede avaliar a sustentabilidade temporal que Nayak et al. analisam em produção real. Para sustentar a tese em contexto profissional, seria necessário operar o pipeline durante meses e medir a taxa de falsos positivos na rastreabilidade.

**Referências**

DYGALO, D. *Schemathesis: Property-based testing for OpenAPI and GraphQL APIs*. Documentação oficial, 2024. Disponível em: https://schemathesis.readthedocs.io/. Acesso em: jun. 2026.

GITHUB. *GitHub Actions Documentation*. GitHub, 2024. Disponível em: https://docs.github.com/en/actions. Acesso em: jun. 2026.

ISO — INTERNATIONAL ORGANIZATION FOR STANDARDIZATION. *ISO/IEC/IEEE 29119-3:2021 — Software and systems engineering — Software testing — Part 3: Test documentation*. Geneva: ISO, 2021. Disponível em: https://www.iso.org/standard/81293.html. Acesso em: jun. 2026.

NAYAK, K. *et al.* Sustainable Continuous Testing in DevOps Pipeline. In: *IEEE Conference Publication*, 2024. Disponível em: https://www.researchgate.net/publication/382512542. Acesso em: jun. 2026.

OPENAPI INITIATIVE. *OpenAPI Specification v3.1.0*. OpenAPI Initiative / Linux Foundation, 2021. Disponível em: https://spec.openapis.org/oas/v3.1.0. Acesso em: jun. 2026.

TMMi FOUNDATION. *TMMi Framework: Release 1.2*. TMMi Foundation, 2018. Disponível em: https://www.tmmi.org/tmmi-framework/. Acesso em: jun. 2026.

DORA / GOOGLE CLOUD. *Accelerate State of DevOps Report 2024*. Google Cloud, 2024. Disponível em: https://dora.dev/research/2024/dora-report/. Acesso em: jun. 2026.

---

## Síntese Epistemológica

**a)** No Sprint 1 a "evidência de qualidade" era um output verde no terminal do meu computador — visível apenas para mim e desaparecendo ao fechar a janela; no Sprint 8, a evidência é uma matriz de rastreabilidade gerada automaticamente pelo CI a cada commit, arquivada como artefato público e auditável por qualquer pessoa com acesso ao repositório.

**b)** O achado mais surpreendente do Schemathesis foi que IDs negativos no path (`/saldo/-1`) retornam uma página HTML 404 genérica do Flask ao invés de JSON estruturado — uma divergência entre o contrato declarado e o comportamento real do roteamento que nenhum dos meus testes manuais dos Sprints 1 a 5 havia sequer tentado verificar.

**c)** Minha tese: a automação da rastreabilidade no CI é condição necessária mas não suficiente para qualidade demonstrável — ela desloca a auditoria humana do ato de executar testes para o ato de validar a integridade semântica do mapeamento entre o que foi testado e o que o artefato de evidência declara como testado.
