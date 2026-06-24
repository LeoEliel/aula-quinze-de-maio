# 🚀 Guia de Estudo e Entrega: Sprints 1 a 8

Olá, Leonardo! Se você precisar explicar este projeto para o seu professor ou revisar o que foi feito de forma rápida, este documento é o seu melhor aliado. Ele resume nossa jornada de forma muito simples e mostra como a pasta do seu computador está organizada agora.

---

## 🧭 O que fizemos até aqui? (A nossa jornada)

1. **Sprints 1 e 2: A Construção (Testes de Componente)**
   * Criamos a base do aplicativo de banco (`app.py`) e fizemos testes para verificar se as funções respondiam corretamente.
   * **Nível/Técnica:** Teste de Componente / Caixa-Preta e Caixa-Branca básica.

2. **Sprint 3: O Teste de Estresse (Testes de Sistema / Propriedades)**
   * Usamos a biblioteca **Hypothesis** para gerar dados automaticamente e tentar quebrar o sistema com entradas aleatórias.
   * **Nível/Técnica:** Teste de Sistema / Caixa-Preta (baseado em propriedades).

3. **Sprint 4: A Caça aos Mutantes (Auditoria dos Testes)**
   * Usamos o **mutmut** para inserir bugs deliberados no código e verificar se nossos testes os detectavam.
   * **Nível/Técnica:** Caixa-Branca Avançada.

4. **Sprint 5: A Solução com BDD (Testes de Aceite / UAT)**
   * Escrevemos cenários em linguagem natural (Gherkin: Dado/Quando/Então) no arquivo `transferencia.feature` e ligamos ao código Python (`test_transferencia.py`).
   * **Nível/Técnica:** Teste de Aceite (UAT) / Caixa-Preta.

5. **Sprint 6: O Fechamento (Compliance Regulatória)**
   * Classificamos todo o projeto de acordo com a norma **BSTQB CTFL v4.0** e adicionamos simulação de regra do Banco Central.
   * **Nível/Técnica:** Teste de Aceite Regulatório.

6. **Sprint 7: Avaliação de Maturidade (TMMi, DORA e Position Paper)**
   * Avaliamos o processo de testes contra o **TMMi v1.2**, calculamos as 4 métricas **DORA 2024** e escrevemos um position paper acadêmico.
   * **Nível/Técnica:** Avaliação de maturidade e produção acadêmica.

7. **Sprint 8: Da Declaração à Demonstração (ISO 29119-3, Schemathesis, CI)**
   * Especificamos formalmente 4 casos de teste pelo padrão **ISO/IEC/IEEE 29119-3:2021**.
   * Escrevemos o `openapi.yaml` como contrato observável da API e rodamos **Schemathesis** (contract testing).
   * Configuramos pipeline **GitHub Actions** com matriz de rastreabilidade automatizada.
   * Escrevemos relatório técnico em diálogo com **Nayak et al. (2024)**.
   * **Nível/Técnica:** Teste de Contrato (Schemathesis) / Rastreabilidade ISO 29119-3 / CI automatizado.

---

## 📁 Estrutura do Projeto

```text
aula-quinze-de-maio/
│
├── .gitignore                          # Ignora caches e arquivos temporários
│
├── references/                         # 📚 Roteiros do professor, PDFs e materiais de referência
│   ├── 03 - Roteiro - sprint 1 - *.pdf
│   ├── 04 - Roteiro - sprint 2 - *.pdf
│   ├── 04 - Roteiro - sprint 3 - *.pdf
│   ├── 05 - Roteiro - sprint 5 - *.pdf
│   ├── Material - 09-05-2026.pdf
│   ├── Material roteiro - 05-06-2026-2.pdf
│   ├── Material roteiro - 13-06-2026.pdf
│   ├── Material roteiro - 17-06-2026.pdf  ← Sprint 8
│   ├── syllabus_ctfl_4.0br.pdf
│   ├── material_roteiro_*.txt          # Versões em texto dos roteiros
│   └── sprint_*_roteiro.txt
│
└── internet_banking_tests/             # 💻 Código-fonte do projeto
    │
    ├── app.py                          # Código principal do Internet Banking (Flask)
    ├── config.py                       # Configurações do banco de dados SQLite
    ├── banking.db                      # Banco de dados SQLite
    ├── openapi.yaml                    # ✨ Sprint 8: Contrato OpenAPI 3.1 da API
    ├── requirements.txt                # ✨ Sprint 8: Dependências consolidadas
    │
    ├── conftest.py                     # Fixture autouse: reseta o banco antes de cada teste
    ├── pytest.ini                      # Configuração do pytest
    ├── setup.cfg                       # Configuração do mutmut
    ├── test_transferencia.py           # Testes BDD ligados ao Gherkin (arquivo canônico)
    │
    ├── .github/workflows/             # ✨ Sprint 8: Pipeline CI
    │   └── test.yml                   # GitHub Actions: testes + Schemathesis + matriz
    │
    ├── features/                       # Cenários BDD em linguagem natural
    │   ├── transferencia.feature       # Cenários de transferência (Dado/Quando/Então)
    │   └── saldo_extrato.feature       # Cenários de consulta de saldo e extrato
    │
    ├── relatorios/                     # 📄 Relatórios do projeto
    │   ├── entregas/                   # ✅ DOCUMENTOS FINAIS PARA ENVIAR NO AVA
    │   │   ├── Relatorio_Sprint4_LeonardoEliel.docx
    │   │   ├── Relatorio_Sprint5_LeonardoEliel.docx
    │   │   ├── Relatorio_Sprint6_LeonardoEliel.docx
    │   │   ├── Relatorio_Sprint7_LeonardoEliel.docx
    │   │   └── Relatorio_Sprint8_LeonardoEliel.docx  ← NOVO
    │   └── rascunhos/                  # 📝 Rascunhos e notas intermediárias (Markdown)
    │       ├── entregaveis_sprint_8.md ← NOVO
    │       └── ... (sprints anteriores)
    │
    ├── scripts/                        # 🔧 Scripts Python utilitários
    │   ├── gera_matriz.py              # ✨ Sprint 8: Gerador de matriz de rastreabilidade
    │   ├── gerar_relatorio_sprint8.py  # ✨ Sprint 8: Gerador do .docx
    │   └── gerar_relatorio_sprint*.py  # Geradores de sprints anteriores
    │
    ├── backups/                        # 🗃️ Backups de código de sprints anteriores
    │
    ├── legacy/                         # ⏳ Testes antigos desativados
    │   ├── test_ia_gerado.py           # Sprint 1: testes gerados pela IA
    │   ├── test_hypothesis.py          # Sprint 3: testes baseados em propriedades
    │   ├── test_hypothesis_extra.py    # Sprint 3: testes extras com Hypothesis
    │   └── test_bdd_sprint5.py         # Sprint 5: versão anterior dos testes BDD
    │
    ├── mutants/                        # 🧬 Diretório de trabalho do mutmut
    │
    └── venv/                           # 📦 Ambiente virtual Python
```

---

## 💡 Resumo do Aprendizado
Ao longo de 8 sprints, aprendemos que **qualidade de software não se declara — se demonstra**. No Sprint 1, a "evidência" era um output verde no terminal. No Sprint 8, é uma matriz de rastreabilidade gerada automaticamente pelo CI a cada commit, arquivada como artefato público e auditável. A virada epistemológica é da **declaração** (Word, reunião) para a **demonstração** (pipeline, artefato gerado, URL pública).
