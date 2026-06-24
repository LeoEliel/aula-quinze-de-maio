# Resumo do Fluxo Completo: Sprints 1 a 6

Este guia consolida o entendimento de toda a jornada de desenvolvimento e testes da sua aplicação de Internet Banking (My Cash Controller) e detalha o que deve ser enviado no AVA.

---

## 🧭 O Fluxo do Projeto (Sprints 1 a 6)

O projeto seguiu uma jornada evolutiva de testes, partindo do código mais simples (caixa-branca de componente) até a validação comportamental (BDD de aceitação) e mapeamento regulatório (compliance).

### 1️⃣ Sprints 1 & 2: O Alicerce (Testes de Componente)
*   **O que fizemos:** Criamos a API Flask básica em `app.py` com rotas para obter saldo, extrato e fazer transferências, conectada a um banco SQLite local (`banking.db`). Escrevemos os primeiros testes unitários básicos no Pytest.
*   **Conceito-chave:** Testes focados em validar se as funções retornavam o esperado de forma direta (caminho feliz).

### 2️⃣ Sprint 3: Testes baseados em Propriedades (Testes de Sistema)
*   **O que fizemos:** Introduzimos a biblioteca **Hypothesis**. Em vez de inventar dados de teste manuais, definimos invariantes de negócio (ex: *"um valor de transferência deve ser sempre positivo"*) e deixamos o Hypothesis gerar automaticamente milhares de combinações de dados inválidos (fuzzing) para tentar quebrar a API.
*   **Conceito-chave:** Troca de testes baseados em exemplos por testes baseados em regras/propriedades gerais de sistema.

### 3️⃣ Sprint 4: Teste de Mutação (Auditoria de Testes / Caixa-Branca)
*   **O que fizemos:** Rodamos o **mutmut** para injetar pequenos "defeitos propositais" (mutantes) em nosso `app.py` (por exemplo, alterando um sinal `<` para `<=`, ou um `==` para `!=`). Descobrimos que alguns mutantes sobreviveram à nossa suíte de testes existente.
*   **Conceito-chave:** A eficácia dos testes não é medida apenas pela cobertura de linha, mas pela capacidade de detectar bugs. Se o mutante sobreviveu, nossos testes anteriores eram **insuficientes**.

### 4️⃣ Sprint 5: Desenvolvimento Guiado por Comportamento (BDD / Aceite)
*   **O que fizemos:** Criamos cenários de comportamento usando a linguagem Gherkin em português (`transferencia.feature`) e os implementamos em Python usando o `pytest-bdd` (no arquivo `test_transferencia.py`). 
*   **O ajuste crucial:** Descobrimos que a IA gerava código usando a biblioteca `requests` (que precisava do servidor rodando na rede). Nós removemos essa dependência de rede e usamos o cliente interno do Flask (`app.test_client()`), permitindo que o `mutmut` rodasse as simulações em memória de maneira veloz. Com os novos cenários BDD cobrindo os limites exatos (ex: transferência de valor igual ao saldo total), **todos os mutantes foram eliminados**.
*   **Conceito-chave:** Uso do BDD para alinhar os testes com as regras de negócio reais, eliminando lacunas de cobertura lógica.

### 5️⃣ Sprint 6: A Re-rotulação Semântica (Epistemologia & Compliance)
*   **O que fizemos:** Não escrevemos código novo. Mapeamos os testes anteriores utilizando o vocabulário oficial do **BSTQB CTFL v4.0** (Níveis e Técnicas de teste). Além disso, escrevemos um cenário em Gherkin focado em **Aceitação Regulatória** (limite de PIX noturno determinado pelo Banco Central) para demonstrar testes de compliance.
*   **Conceito-chave:** Profissionalização teórica e adequação a requisitos regulatórios governamentais.

---

## 📦 O que você deve entregar no AVA

Para fechar a Unidade 2, você precisa fazer as entregas das **Sprints 4, 5 e 6**. Recomenda-se gerar um arquivo Word compilado (ou PDFs individuais) para enviar na plataforma.

### 📄 Checklist de Entregáveis por Sprint

#### 1. Relatório da Sprint 4 (Mutação)
*   [ ] Lista dos mutantes que sobreviveram na execução inicial.
*   [ ] Classificação técnica (segundo Papadakis et al., 2019) se eles sobreviveram por **Insuficiência de Testes** (falta de cobertura lógica) ou se eram **Mutantes Equivalentes** (que não alteram a resposta do sistema).

#### 2. Relatório da Sprint 5 (BDD / pytest-bdd)
*   [ ] O arquivo Gherkin em português: `features/transferencia.feature`.
*   [ ] O arquivo de passos em Python: `test_transferencia.py`.
*   [ ] Justificativa de regras de negócio traduzidas para os mutantes que haviam sobrevivido.
*   [ ] A **Revisão Crítica** explicando a "escorregada" da IA ao tentar usar conexões HTTP externas (biblioteca `requests`) e como corrigimos isso usando o `app.test_client()` do Flask (baseando-se em *Coutinho e Nascimento, 2025*).
*   [ ] Print/Log do Pytest dando PASSED nos testes de transferência.
*   [ ] Print/Log do Mutmut mostrando os mutantes KILLED.

#### 3. Relatório da Sprint 6 (Teoria & BACEN)
*   [ ] Mapeamento dos Níveis de Teste (Componente, Integração, Sistema, Aceite) segundo o Syllabus CTFL v4.0.
*   [ ] Mapeamento das Técnicas de Teste (Caixa-Preta, Caixa-Branca, Experiência).
*   [ ] O Cenário Gherkin representando a regra regulatória do Banco Central (PIX noturno de até R$ 5.000,00).
*   [ ] A **Tabela Epistemológica** cruzando: *Artefato → Nível → Técnica → Ferramenta → Métrica*.

*(Nota: Todos os dados textuais simplificados para essas três sprints já estão salvos e estruturados nos arquivos `entregaveis_sprint_5.md`, `entregaveis_sprint_6.md` e nos arquivos `.docx` na pasta do seu projeto. Você pode copiar o conteúdo diretamente deles).*
