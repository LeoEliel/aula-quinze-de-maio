# RELATÓRIO PRELIMINAR: SPRINT 7 — CONFRONTO COM A LITERATURA E POSITION PAPER
## DISCIPLINA: TESTE DE SOFTWARE — SISTEMA DE INTERNET BANKING
**Aluno:** Leonardo Eliel Dias da Silva  
**Professor/Orientador:** Dr. Claudinei de Oliveira  
**Instituição:** Instituto Federal de Rondônia — IFRO  

---

### CAMADA 3: CONFRONTO CRÍTICO COM A LITERATURA CIENTÍFICA

#### Investigação Técnica 3 — Respostas ao Estudo de El Haji, Brandt e Zaidman (2024)

##### a) Usabilidade Baixa dos Testes Gerados por IA e Evidências Empíricas
* **Achado Científico:** Os autores observaram que a usabilidade dos testes gerados pela IA (instanciada como Google Gemini em nosso projeto) é baixa, exigindo constantes refatorações manuais por parte dos desenvolvedores.
* **Evidência Prática (Sprint 1):** A suíte `test_ia_gerado.py` gerada pela IA inicialmente utilizava chamadas HTTP reais via biblioteca `requests` e foi incapaz de modelar o isolamento do banco SQLite (`banking.db`). Na segunda execução consecutiva, o saldo da conta já estava alterado (sujo), resultando em falhas dos testes por quebra do princípio de independência.
* **Evidência Prática (Sprint 5):** Ao implementar o BDD, a IA tentou redefinir fixtures redundantes e gerou códigos usando requisições externas para testar os cenários de transferência. Foi necessário reescrever o código de passos para usar o cliente interno do Flask (`app.test_client()`) em memória, o que evitou dependências de rede e viabilizou a execução veloz dos testes de mutação.

##### b) Melhoria com Exemplos e Relação com a Estrutura de Conftest
* **Achado Científico:** A qualidade das sugestões da IA aumenta significativamente quando já existem testes estruturados na mesma classe ou arquivo de contexto, permitindo que a IA os mimetize.
* **Evidência Prática (Sprint 2):** Ao criarmos manualmente o arquivo `conftest.py` com a fixture `autouse=True` para reinicializar o banco SQLite, estabelecemos um padrão arquitetural claro. Nas sprints subsequentes (3 e 5), a IA foi capaz de construir os testes baseados em propriedades (Hypothesis) e vincular as fixtures do pytest-bdd de maneira muito mais assertiva e estável, demonstrando que as LLMs funcionam com maior eficácia quando alimentadas com um contexto de engenharia bem desenhado pelo testador.

##### c) O Gemini como Ferramenta de Assistência versus Autoridade Inquestionável
* **Evidência Prática de Violação:** O momento crítico em que o Google Gemini foi incorretamente tratado como uma autoridade ocorreu na transição da Sprint 1 para a Sprint 2. Confiou-se cegamente que a IA havia coberto o cenário limite da transferência com saldo igual ao valor, porque os testes deram "passou". No entanto, a IA havia omitido a verificação física dos saldos após as transações (validando apenas o status HTTP 200). Isso mostrou que a IA atuou como uma autoridade sintática passiva, cobrindo linhas sem garantir a integridade semântica contábil do banco de dados, o que foi auditado e exposto apenas quando rodamos o teste de mutação na Sprint 4.

---

### Investigação Técnica 4 — Position Paper

**Título:** A Ilusão da Cobertura Sintática: Por que o TMMi v1.2 e o DORA 2024 Devem Priorizar o Mutation Score como Métrica de Maturidade na Era dos Modelos de Linguagem

A disseminação de ferramentas de IA generativa de código, como o Google Gemini, acelerou o processo de codificação de testes, mas introduziu riscos graves de qualidade. A cobertura de declarações (Statement Coverage), embora amplamente utilizada no TMMi Level 2 e associada à velocidade (throughput) no DORA, tornou-se uma métrica de vaidade incapaz de detectar falhas lógicas sutis geradas por LLMs. Defende-se que o TMMi e o DORA devem reformular seus critérios de maturidade, elevando o Mutation Score (teste de mutação) de uma prática avançada para uma métrica obrigatória de estabilidade (stability) no início do ciclo de desenvolvimento de software assistido por IA.

Essa tese baseia-se na evolução da suíte de testes da API de Internet Banking (My Cash Controller) ao longo das Sprints 1 a 5. Na Sprint 1, os testes unitários reativos gerados pela IA alcançaram cobertura linear, mas falharam sistematicamente na repetibilidade devido à persistência em disco do SQLite e à dependência de conexões de rede HTTP em `test_ia_gerado.py`. Corrigido esse acoplamento arquitetural nas Sprints 2 e 4 (usando `app.test_client()` em memória), o teste de mutação via `mutmut` revelou que 100% dos mutantes estruturais não-equivalentes (tais como a inversão lógica na verificação de saldo de `conta_origem["saldo"] < valor` para `<= valor`) sobreviveram à suíte anterior. Somente com a introdução do BDD na Sprint 5 (`features/transferencia.feature`) e o mapeamento explícito de regras de negócio, os mutantes foram eliminados. A cobertura convencional de linhas não revelou as vulnerabilidades que apenas o Mutation Score capturou.

Estes achados corroboram o estudo empírico de El Haji, Brandt e Zaidman (2024), que apontam a usabilidade insatisfatória de testes autônomos gerados por LLMs em Python. Como os autores demonstram, a IA (instanciada como Google Gemini em nosso contexto) atua como um mimetizador de padrões locais que necessita de intervenção de especialistas para ajustar dependências arquiteturais e contextuais. Ademais, o declínio de 7,2% em estabilidade de entrega observado no *Accelerate State of DevOps Report* (DORA, 2024) em equipes com alta adoção de IA reflete esse cenário de "saturação de testes frágeis". O trabalho de Yuan et al. (2024) reforça essa perspectiva ao provar que LLMs carecem de entendimento semântico profundo das regras de negócio, gerando asserções redundantes ou tautológicas que fingem cobrir o código, mas não interceptam bugs reais.

Propõe-se uma reformulação metodológica no TMMi v1.2 e no framework DORA. No TMMi, a área de processo *Test Design and Execution* (Level 2) deve exigir o teste de mutação em caráter obrigatório sempre que ferramentas de IA forem empregadas para gerar código ou testes. No DORA, propõe-se incluir a métrica *Mutation Failure Rate* (MFR) na dimensão de Estabilidade (Stability) de software. O MFR atuaria como um portão de qualidade automatizado em pipelines de Integração Contínua (CI), bloqueando deploys cujo Mutation Score seja inferior a 80% dos mutantes matáveis. Isso desencoraja a aceitação cega de testes automatizados ineficazes criados por LLMs e força o refinamento conceitual dos testes antes de chegarem à produção.

Reconhece-se que a adoção em larga escala do teste de mutação obrigatório enfrenta restrições operacionais graves, devido ao elevado custo computacional requerido para executar repetidas vezes a suíte de testes sob mutações no código-fonte. Em sistemas monolíticos complexos, essa abordagem pode comprometer a métrica de *Lead Time for Changes*. Estudos futuros devem avaliar a viabilidade de testes de mutação preditivos ou restritos apenas ao escopo das alterações (diff mutation testing) para viabilizar a proposta em esteiras ágeis.

#### Referências Bibliográficas

* DORA / GOOGLE CLOUD. **Accelerate State of DevOps Report 2024**. Google Cloud, 2024. Disponível em: <https://dora.dev/research/2024/dora-report/>. Acesso em: 17 jun. 2026.
* EL HAJI, K.; BRANDT, C.; ZAIDMAN, A. Using GitHub Copilot for Test Generation in Python: An Empirical Study. In: **ACM/IEEE International Conference on Automation of Software Test (AST)**, 5., 2024, Lisbon. Proceedings... New York: ACM, 2024. p. 45-55. DOI: 10.1145/3644032.3644443.
* LI, Y. et al. Evaluating large language models for software testing. **Computer Standards & Interfaces**, v. 93, 103942, 2025. DOI: 10.1016/j.csi.2024.103942.
* TMMi FOUNDATION. **TMMi Framework: Release 1.2**. TMMi Foundation, 2018. Disponível em: <https://www.tmmi.org/tmmi-framework/>. Acesso em: 17 jun. 2026.
* VAN VEENENDAAL, E. Test Maturity Model integration (TMMi): Test Maturity in the Financial Domain. **American Journal of Computer Science and Technology**, v. 7, n. 2, 2024. DOI: 10.11648/j.ajcst.20240702.13.
* YUAN, Z. et al. Evaluating and Improving ChatGPT for Unit Test Generation. **Proceedings of the ACM on Software Engineering**, v. 1, n. FSE, 2024. DOI: 10.1145/3660783.

---

### SÍNTESE EPISTEMOLÓGICA (REGISTRO FINAL)

* **a) Qual é a diferença operacional entre "saber o nome do que produzi" (Sprint 6) e "saber o nível de maturidade do que produzi" (Sprint 7)?**
  Saber o nome do que produzi (Sprint 6) é um exercício léxico e de classificação taxonômica básica sob a CTFL do BSTQB. Saber o nível de maturidade (Sprint 7) é um diagnóstico sistêmico e quantitativo que confronta o processo como um todo frente a falhas (mutantes sobreviventes), eficácia de equipe (DORA) e conformidade setorial real (TMMi), transformando o teste em ferramenta de gestão de riscos e governança.
* **b) Que número DORA mais lhe surpreendeu ao calcular sobre os seus dados, e por quê?**
  O Mean Time to Recovery (MTTR) de apenas 40 minutos. Surpreendeu-me ver como a aplicação estrita de técnicas de ciclo de vida e independência com fixtures do pytest permite isolar e restaurar a estabilidade do código de forma quase instantânea se comparado a ambientes industriais lentos, evidenciando o poder de ferramentas locais de desenvolvimento para feedbacks velozes.
* **c) Em uma frase, qual é a sua tese para o position paper — antes mesmo de escrevê-lo?**
  A cobertura de código convencional tornou-se uma métrica ineficaz na era da geração automática de testes por modelos de linguagem, tornando obrigatória a inclusão do Mutation Score como critério essencial de maturidade no TMMi e DORA.
