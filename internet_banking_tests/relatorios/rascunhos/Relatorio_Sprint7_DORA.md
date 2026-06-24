# RELATÓRIO PRELIMINAR: SPRINT 7 — MÉTRICAS DORA 2024
## DISCIPLINA: TESTE DE SOFTWARE — SISTEMA DE INTERNET BANKING
**Aluno:** Leonardo Eliel Dias da Silva  
**Professor/Orientador:** Dr. Claudinei de Oliveira  
**Instituição:** Instituto Federal de Rondônia — IFRO  

---

### CAMADA 2: CÁLCULO NUMÉRICO DAS QUATRO MÉTRICAS-CHAVE DO DORA 2024

Aplicando os conceitos do *Accelerate State of DevOps Report 2024* aos dados históricos reais dos Sprints 1 a 6, realizamos o cálculo numérico das quatro métricas-chave. Para viabilizar a medição, traduzimos os conceitos de produção de software para o contexto acadêmico e de desenvolvimento da nossa suíte de testes.

#### 1. Cálculo Detalhado das Métricas

##### a) Lead Time for Changes (Tempo de Lead Time para Mudanças)
* **Definição Operacional:** O tempo decorrido entre a publicação do roteiro contendo a especificação da questão Q8 (09-05-2026) e a primeira versão funcional dos testes passando no pytest (`test_ia_gerado.py` no Sprint 1).
* **Cálculo Baseado em Timestamps:**
  * Postagem da especificação: **09-05-2026 às 08:00:00**
  * Conclusão do `test_ia_gerado.py`: **22-05-2026 às 20:13:00** (conforme timestamp do arquivo).
  * Intervalo: **13 dias, 12 horas e 13 minutos** (aproximadamente **324,2 horas**).
* **Valor:** **13,5 dias (324 horas)**

##### b) Deployment Frequency (Frequência de Deploy)
* **Definição Operacional:** O número médio de pacotes funcionais de testes (entregas de sprints) publicados no Ambiente Virtual de Aprendizagem (AVA) por semana.
* **Cálculo:**
  * Total de entregas (Sprints 1 a 6): **6 deploys**
  * Período total do projeto: **4 semanas** (de 15-05-2026 a 12-06-2026).
  * Frequência: 6 entregas / 4 semanas = **1,5 entregas por semana**.
* **Valor:** **1,5 deploys por semana** (cadência média de 1 deploy a cada 4,6 dias).

##### c) Change Failure Rate (Taxa de Falha de Mudanças)
* **Definição Operacional:** A razão entre o número de falhas não detectadas que "escaparam" para o ambiente simulando produção (mutantes sobreviventes que alteram o comportamento do sistema) e o total de mutantes gerados.
* **Cálculo:**
  * Na Sprint 4, executamos o `mutmut` que gerou **7 mutantes estruturais**.
  * Inicialmente, devido à acoplagem de rede (uso da biblioteca `requests` pela IA), a suíte não rodava no sandbox e **todos os 7 mutantes sobreviveram** (100% de falha).
  * Com a refatoração do BDD na Sprint 5 (uso de `app.test_client()`), matamos **5 mutantes** de insuficiência, restando apenas **2 mutantes equivalentes** (que não alteram o comportamento do sistema).
  * Desconsiderando mutantes equivalentes (conforme Papadakis et al., 2019), o Change Failure Rate inicial da suíte da IA era de **100%** (3 mutantes de insuficiência vivos de 3 possíveis). Após os ajustes da Sprint 5, essa taxa caiu para **0%** de falhas de insuficiência sobreviventes.
* **Valor:** **100% na suíte original da IA (Sprint 4)** | **0% na suíte final ajustada com BDD (Sprint 5)** (desconsiderando mutantes equivalentes).

##### d) Mean Time to Recovery - MTTR (Tempo Médio de Recuperação)
* **Definição Operacional:** O tempo necessário para restaurar a estabilidade do sistema após a detecção de uma falha de isolamento. Medido entre a primeira falha consecutiva do teste `test_transferencia_saldo_igual_valor` (causada pelo estado poluído do banco SQLite na Sprint 1) e a sua correção definitiva via fixture no `conftest.py` (Sprint 2).
* **Cálculo Baseado em Timestamps:**
  * Conclusão da Sprint 1 (falha documentada): **22-05-2026 às 20:14:00**
  * Conclusão da Sprint 2 (correção aplicada): **22-05-2026 às 20:54:00** (conforme timestamps dos respectivos arquivos).
  * Intervalo: **40 minutos** (ou **0,67 horas**).
* **Valor:** **40 minutos (0,67 horas)**

---

### PLANILHA DE MÉTRICAS DORA (MODELO EXPORTADO)

| Métrica DORA | Definição Operacional Acadêmica | Valor Calculado (Sprints 1-6) | Cluster Sugerido e Justificativa |
| :--- | :--- | :--- | :--- |
| **Lead Time for Changes** | Tempo entre a publicação da especificação e o código de testes passar no pytest | **13,5 dias** | **Medium Performer** (Fica na faixa de 1 a 2 semanas para mudanças passarem de especificação a deploy). |
| **Deployment Frequency** | Frequência de sprints com artefatos funcionais entregues no AVA por semana | **1,5 deploys/semana** | **High Performer** (A equipe mantém uma cadência constante de deploy menor que uma semana). |
| **Change Failure Rate** | Razão entre mutantes de insuficiência que sobreviveram e os mutantes matáveis | **100% (Sprint 4)**<br>**0% (Sprint 5)** | **Low Performer (Sprint 4)** -> **Elite Performer (Sprint 5)** (A suíte inicial de IA deixava bugs passarem, mas o BDD blindou o código). |
| **Mean Time to Recovery** | Tempo entre a falha por sujeira de banco e a correção via fixture autouse | **40 minutos** | **Elite Performer** (A restauração do ambiente após a detecção do erro de isolamento levou menos de uma hora). |

#### Conclusão e Posicionamento nos Clusters DORA

Se o desenvolvimento da suíte de testes do *My Cash Controller* fosse conduzido por uma equipe real de engenharia de software em ambiente de produção, o time se posicionaria globalmente como **Medium Performer**.

**Justificativa:** 
Embora a frequência de entrega (**High**) e o tempo de recuperação de falhas no laboratório (**Elite**) indiquem alta agilidade e capacidade rápida de resposta, a equipe é limitada pelo *Lead Time* de entrega (**Medium**) e, crucialmente, pela taxa de falha inicial de alterações (**Low** na Sprint 4). A introdução de código gerado por IA sem testes adequados de mutação representou um risco severo de vazamento de bugs (100% de mutantes sobreviventes). A transição para o uso de BDD e testes em memória na Sprint 5 reduziu a taxa de falha de segurança para **0%** (nível **Elite**), porém, na média histórica das sprints, o time permanece consolidado no cluster **Medium Performer**, o que se alinha com a ausência de um pipeline totalmente automatizado de CI/CD e de esteiras automáticas de deploys em produção.
