# RELATÓRIO TÉCNICO: SPRINT 1 — IA VERSUS ESPECIFICAÇÃO DE TESTES
## DISCIPLINA: TESTE DE SOFTWARE — SISTEMA DE INTERNET BANKING
**Aluno:** Leonardo Eliel Dias da Silva  
**Professor/Orientador:** Dr. Claudinei de Oliveira  
**Instituição:** Instituto Federal de Rondônia — IFRO  
**Ambiente Virtual:** venv (Python 3.14, Flask, Pytest, Requests)  

---

### PASSO 1: RESPOSTA DA QUESTÃO 8 (SUSTENTAÇÃO TEÓRICA)
* **Texto Completo Copiado da Especificação Humana:**
  > "Primeiro teste: verificação de transferência com saldo suficiente. Abordagem TDD (RAHMAN et al., 2024, p. 52): escrever o teste antes da função - o teste define que transfer(conta_origem, conta_destino, valor) deve retornar sucesso quando saldo >= valor. Caso de borda: saldo exatamente igual ao valor da transferência (condição de fronteira conecta com técnica de caixa-preta vista nas semanas anteriores). O que o teste verifica antes do código: a especificação do comportamento esperado, não a implementação. Categoria de framework: ferramenta de execução de testes unitários (BSTQB, 2023, p. 52)."

---

### PASSO 4: PERGUNTAS PARA INVESTIGAÇÃO EMPÍRICA (FALHA DE ISOLAMENTO)

#### **a) Que decisão do `app.py` viabiliza essa diferença de comportamento entre execuções consecutivas?**
No arquivo `app.py` (linhas 25-47), a inicialização do banco de dados através da função `init_db()` utiliza instruções SQL condicionais do tipo `CREATE TABLE IF NOT EXISTS` e povoa os registros usando `INSERT OR IGNORE`. O SQLite é configurado para persistir fisicamente em disco no arquivo `banking.db`.
O servidor Flask, rodando de forma persistente, mantém esse arquivo físico aberto e mutável entre as requisições consecutivas. 
Os testes unitários em `test_ia_gerado.py` realizam requisições HTTP reais que causam mutações definitivas de estado no banco (debitando saldos). No primeiro run, o teste `test_transferencia_saldo_igual_valor` transfere com sucesso R$ 1000.00 da Conta 1 (Alice), reduzindo seu saldo a R$ 0.00. Como a transação é persistida em disco, na segunda execução consecutiva dos testes, a Conta 1 inicia com saldo zerado, fazendo com que a API Flask recuse a transação com `HTTP 422 - saldo insuficiente`, quebrando o teste.

#### **b) Que característica de "bom caso de teste" (ISTQB CTFL v4.0.1) está sendo violada pelos testes gerados pela IA?**
Está sendo violada a **Independência de Testes (Isolamento)**. Conforme o Syllabus oficial do Certified Tester Foundation Level (BSTQB, 2023, Capítulo 6, p. 52-53), os testes automáticos devem ser totalmente independentes e livres de efeitos colaterais. O resultado de um caso de teste não deve depender do histórico, da ordem de execução, nem da sujeira residual deixada por execuções de testes anteriores. Cada caso de teste deve garantir a integridade de seu próprio estado ("setup" e "teardown").

#### **c) Essa violação estava prevista na sua resposta da Q8 ou foi uma omissão tanto sua quanto da ferramenta?**
Foi uma **omissão de ambas as partes**. Na especificação humana da Q8, limitou-se a modelar os critérios lógicos e caixa-preta da transferência (a análise de fronteira de saldo). O especificador humano omitiu os requisitos não-funcionais de infraestrutura de rede, concorrência e gerenciamento do ciclo de vida do estado físico do banco de dados SQLite. A ferramenta de IA, operando de forma estritamente reativa e sintática, apenas traduziu os enunciados para requisições procedurais usando a biblioteca `requests`, sem considerar o ciclo de vida do ambiente ou sugerir mecanismos de reset de dados.

---

### PASSO 5: TABELA DE CRITÉRIOS TÉCNICOS (SPRINT 1)

| Critério Técnico | Presente? | Linha(s) no Código | Observação Técnica |
| :--- | :---: | :---: | :--- |
| **Cenário principal da Q8 coberto** | **Sim** | Linhas 23 - 32 | Coberto pela função `test_transferencia_valida` (transferência bem-sucedida padrão). |
| **Caso de borda identificado na Q8** | **Sim** | Linhas 34 - 43 | Coberto por `test_transferencia_saldo_igual_valor` com comentário explícito `# Primeiro teste TDD`. |
| **Teste de saldo insuficiente** | **Sim** | Linhas 44 - 50 | Coberto por `test_transferencia_saldo_insuficiente` enviando R$ 9999.00. |
| **Teste de conta inexistente (404)** | **Sim** | Linhas 17-20, 76-83 | Cobertos no saldo (`test_saldo_conta_inexistente`) e na transferência (`test_transferencia_conta_origem_inexistente`). |
| **Teste de valor negativo ou zero** | **Sim** | Linhas 52-59, 60-67 | Cobertos por `test_transferencia_valor_negativo` (-50.0) e `test_transferencia_valor_zero` (0.0). |
| **Teste de mesma conta origem/destino** | **Sim** | Linhas 84 - 91 | Coberto por `test_transferencia_mesma_conta` retornando `HTTP 422`. |
| **Fixture de isolamento (setup/teardown)**| **Não** | — | **Omissão da IA:** Nenhuma fixture do pytest ou reset de dados SQLite foi gerado no arquivo. |
| **Verificação de saldo após transferência** | **Não** | — | **Omissão da IA:** A IA apenas verifica a resposta JSON do POST `/transferencia`, sem validar se o banco de fato debitou e creditou. |

---

### PASSO 6: ANÁLISE DETALHADA DOS "NÃOS" (CENÁRIOS OMITIDOS)

#### 1. Fixture de isolamento (setup/teardown)
* **Relevância no Domínio Bancário:** Sistemas de missão crítica financeira exigem determinismo e repetibilidade impecável em seus ambientes de integração contínua (CI/CD). 
* **Consequência da Omissão em Produção:** Ocorre a instabilidade de testes ("flaky tests"). Os desenvolvedores perdem a confiança na suíte de testes porque ela gera falsos negativos frequentemente devido a banco de dados "sujo". Isso faz com que erros reais de código em produção passem despercebidos sob a suposição errônea de que a falha é apenas um problema de ambiente.

#### 2. Verificação de saldo após transferência
* **Relevância no Domínio Bancário:** É o princípio supremo de integridade contábil e conservação de ativos. Validar que a resposta HTTP retornou `200 OK` comprova apenas a integridade da camada de rede, mas não prova que a gravação física no banco foi concluída sem distorções de arredondamento ou perdas parciais.
* **Consequência da Omissão em Produção:** Risco iminente de criação de "dinheiro fantasma" ou desvios de saldo indetectados. Se houver uma falha interna na lógica aritmética do banco de dados (arredondamento), o sistema pode reportar sucesso ao cliente final mas aplicar valores incorretos no banco de dados, gerando graves passivos fiscais e operacionais.

---

### PASSO 7: COMPARAÇÃO DO OUTPUT DA IA COM A Q8
* **O que a IA gerou que você não havia descrito:** A IA expandiu o escopo de forma autônoma, gerando testes completos para o endpoint `GET /saldo` (contas existentes/inexistentes), validação de campos JSON ausentes (`test_transferencia_campos_ausentes`), e histórico de extratos `GET /extrato` (contas existentes/inexistentes).
* **O que você descreveu e a IA não gerou:** O especificador humano propôs uma visão conceitual baseada em TDD enfocando o design lógico e as boas práticas de frameworks unitários. A IA omitiu totalmente o controle do estado do banco e a persistência, limitando-se a disparar requisições.
* **O que a IA gerou diferente da sua especificação:** O especificador pretendia criar uma especificação que validasse o comportamento esperado antes do código ser codificado (caixa-preta). A IA inverteu o paradigma ao gerar asserções baseadas rigidamente nas strings de erros e status literais existentes no código real da API, atuando como caixa-branca passiva.

---

### REFLEXÃO DO SPRINT 1 (Leonardo Eliel Dias da Silva)

#### **1. Antes de ver o código gerado, você esperava que a IA cobrisse tudo o que você especificou na Q8? O que te surpreendeu - para mais ou para menos?**
*Resposta:* Não esperava que a IA cobrisse todos os pontos de forma tão rápida. Fiquei muito surpreso positivamente (para mais) com a capacidade da IA de mapear com exatidão os payloads JSON e deduzir as mensagens de erro exatas declaradas no servidor Flask (como "Conta nao encontrada" e "Valor deve ser positivo") sem precisar de instrução prévia explícita. Por outro lado, surpreendeu negativamente (para menos) a sua total ingenuidade em relação à dependência física do banco de dados SQLite.

#### **2. Qual foi a diferença mais relevante entre o que você descreveu e o que a IA produziu? Por que essa diferença importa para um sistema bancário real?**
*Resposta:* A diferença mais crítica foi a ausência de verificação real de saldos pós-transação e a falta de um reset do banco de dados (isolamento). Para um banco real, essa omissão representa o risco de se validar uma API que responde com sucesso na web, mas que por baixo dos panos está gravando saldos corrompidos ou errôneos na base de dados principal, gerando prejuízos contábeis silenciosos.

#### **3. Com base no que você leu em COUTINHO; NASCIMENTO (2025), o comportamento da IA que você observou é esperado ou inesperado? Cite a página.**
*Resposta:* O comportamento é plenamente **esperado**. Segundo Coutinho & Nascimento (2025) na **página 12**, a automação de testes depende diretamente da estruturação rigorosa do ambiente de teste e controle de dados. Sem o devido setup e controle de infraestrutura, a automação torna-se frágil, imprevisível e passível de falhas de isolamento, exatamente como ocorreu no teste consecutivo.

#### **4. Em uma linha: qual é o limite fundamental da IA nesse tipo de tarefa?**
*Resposta:* O limite fundamental da IA é a falta de visão sistêmica de arquitetura e infraestrutura, operando como um tradutor sintático local que ignora o ciclo de vida e a persistência do ambiente externo.
