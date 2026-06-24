# RELATÓRIO PRELIMINAR: SPRINT 7 — AVALIAÇÃO DE MATURIDADE (TMMi)
## DISCIPLINA: TESTE DE SOFTWARE — SISTEMA DE INTERNET BANKING
**Aluno:** Leonardo Eliel Dias da Silva  
**Professor/Orientador:** Dr. Claudinei de Oliveira  
**Instituição:** Instituto Federal de Rondônia — IFRO  

---

### CAMADA 1: AUTOAVALIAÇÃO DE MATURIDADE DO PROCESSO DE TESTE (TMMi v1.2)

Com base no histórico empírico de desenvolvimento dos Sprints 1 a 6 e na estrutura atual da suíte de testes do *My Cash Controller*, foi realizada a autoavaliação do processo em relação às áreas de processo do **TMMi Level 2 (Managed)**. A classificação foi pautada pelo princípio da honestidade diagnóstica, exigindo evidência prática e artefatos reais para cada atribuição.

#### 1. Avaliação Detalhada por Área de Processo (TMMi Level 2)

##### a) Test Policy and Strategy (Política e Estratégia de Teste)
* **Status:** **NÃO ATINGIDO**
* **Justificativa:** A suíte de testes carece de um documento formal ou diretriz explícita que defina a política de testes da organização ou a estratégia de execução de longo prazo. Embora tivéssemos critérios técnicos de aceitação descritos nos enunciados das tarefas escolares, os testes foram concebidos de forma puramente reativa e sob demanda. Não há uma governança estruturada de testes na pasta do projeto.

##### b) Test Planning (Planejamento de Teste)
* **Status:** **NÃO ATINGIDO**
* **Justificativa:** A concepção e a escrita dos testes ocorreram de forma incremental e reativa, adaptando-se sprint a sprint conforme as novas funcionalidades eram propostas. Não houve a elaboração prévia de um Plano de Testes abrangente que estimasse cronogramas, esforço de equipe, alocação de recursos físicos/humanos ou análise antecipada de riscos do processo de teste.

##### c) Test Monitoring and Control (Monitoramento e Controle de Testes)
* **Status:** **ATINGIDO**
* **Justificativa:** Há monitoramento contínuo e quantitativo sobre a qualidade e a eficácia da suíte de testes. A cobertura de declarações foi aferida de forma sistemática nas Sprints 2 e 4 através do `pytest-cov` (comando `--cov-report=term-missing`). Além disso, o Mutation Score (porcentagem de mutantes eliminados) foi controlado ativamente na Sprint 4 e Sprint 5 com o uso do `mutmut`, garantindo métricas objetivas de sensibilidade.

##### d) Test Design and Execution (Design e Execução de Testes)
* **Status:** **ATINGIDO**
* **Justificativa:** Aplicamos técnicas formais reconhecidas pelo mercado para o desenho dos casos de teste. Cita-se como evidência:
  * **Técnica de Caixa-Preta (Análise de Valor de Fronteira):** aplicada nos cenários limite de saldo da Q8 no Sprint 1 e nos limites críticos do BDD (Sprint 5), testando transferências com saldo exatamente igual ao valor da transferência.
  * **Property-Based Testing (Teste Baseado em Propriedades):** executado com a biblioteca `Hypothesis` no arquivo `test_hypothesis.py` (Sprint 3) para validar invariantes universais em escala.
  * **Caixa-Branca estrutural:** executada com cobertura de código e testes de mutação.

##### e) Test Environment (Ambiente de Teste)
* **Status:** **ATINGIDO**
* **Justificativa:** O projeto conta com um ambiente de testes rigorosamente controlado, isolado e repetível. A configuração está centralizada em `config.py` (externalizando a conexão do banco de dados SQLite) e o isolamento físico do estado é garantido pelo arquivo `conftest.py` (Sprint 2) através de uma fixture `autouse=True` que recria a tabela e repopula os dados padrão antes de cada execução, prevenindo a instabilidade de testes (*flaky tests*).

---

#### 2. Nível TMMi Alcançado e Comparação com o Benchmark

* **Nível TMMi Atual do Projeto:** **Level 1 (Initial)**
* **Comparação com o Benchmark Setorial:** O survey internacional realizado por **Van Veenendaal (2024)** com 60 instituições financeiras globais estabeleceu o **TMMi Level 3 ("Defined")** como o patamar modal (nível mais comum e esperado) do setor bancário. 
* **Diagnóstico Crítico:** Embora a nossa suíte de testes possua práticas técnicas avançadas de nível 2 (Monitoramento de Cobertura, Ambiente Controlado, Design por BDD e Propriedades) e até práticas associadas ao nível 4 (Testes de Mutação quantitativos), a ausência de **Planejamento de Testes** e **Políticas/Estratégias de Testes** nos impede formalmente de obter a certificação de **TMMi Level 2 (Managed)**. De acordo com as regras de conformidade do modelo TMMi, para que um nível seja atingido, todas as suas respectivas áreas de processo devem estar plenamente satisfeitas. Assim, nossa suíte posiciona-se no **Level 1 (Initial)**, evidenciando uma lacuna organizacional que precisaria ser mitigada com documentação estratégica e planejamento formal para alcançar o benchmark modal do setor financeiro (Level 3).
