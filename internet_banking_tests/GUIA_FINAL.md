# 🚀 Guia de Estudo e Entrega: Sprints 1 a 6

Olá, Leonardo! Se você precisar explicar este projeto para o seu professor ou revisar o que foi feito de forma rápida, este documento é o seu melhor aliado. Ele resume nossa jornada de forma muito simples e mostra como a pasta do seu computador está organizada agora.

---

## 🧭 O que fizemos até aqui? (A nossa jornada)

1. **Sprints 1 e 2: A Construção (Testes de Componente)**
   * **O que fizemos:** Criamos a base de um aplicativo de banco (`app.py`), onde os clientes podem ver saldo, extrato e transferir dinheiro. Fizemos testes simples para ver se as telas e funções respondiam corretamente.
   * **Nível/Técnica:** Teste de Componente / Caixa-Preta e Caixa-Branca básica.

2. **Sprint 3: O Teste de Estresse (Testes de Sistema / Propriedades)**
   * **O que fizemos:** Usamos uma ferramenta chamada **Hypothesis** para gerar dados malucos (fuzzing) automaticamente. Nós dissemos para ele: *"Olha, o valor da transferência nunca pode ser zero ou negativo"*. O Hypothesis então tentou milhares de vezes "quebrar" nosso aplicativo enviando dados estranhos para achar falhas ocultas.
   * **Nível/Técnica:** Teste de Sistema / Caixa-Preta (baseado em propriedades).

3. **Sprint 4: A Caça aos Mutantes (Auditoria dos Testes)**
   * **O que fizemos:** Usamos o **mutmut** para simular bugs no nosso código (tipo trocar um sinal de `<` por `<=` de propósito). Vimos que alguns desses bugs passavam despercebidos pelos nossos testes anteriores.
   * **Nível/Técnica:** Caixa-Branca Avançada.

4. **Sprint 5: A Solução com BDD (Testes de Aceite / UAT)**
   * **O que fizemos:** Escrevemos historinhas sobre como o banco deve se comportar usando linguagem natural (Dado/Quando/Então) no arquivo `transferencia.feature`. Depois, ligamos essas historinhas a testes em Python (`test_transferencia.py`).
   * **O grande acerto:** Corrigimos um erro comum sugerido por Inteligências Artificiais. Elas tentam testar usando conexões de internet (`requests`), o que deixa os testes lentos e instáveis. Nós ajustamos para rodar direto na memória do computador (`app.test_client()`), o que permitiu ao `mutmut` rodar rápido e **eliminar todos os bugs remanescentes**.
   * **Nível/Técnica:** Teste de Aceite (UAT) / Caixa-Preta.

5. **Sprint 6: O Fechamento (Compliance Regulatória)**
   * **O que fizemos:** Classificamos todo o projeto de acordo com a norma oficial internacional de testes (**BSTQB CTFL v4.0**). Também escrevemos uma simulação de regra do Banco Central (teto de R$ 5.000,00 para transações PIX à noite) para demonstrar como o sistema obedece a leis governamentais.
   * **Nível/Técnica:** Teste de Aceite Regulatório.

---

## 📁 Como ficou a nossa pasta de arquivos? (Árvore de Diretórios)

Deixamos tudo bem limpo e organizado. Veja onde está cada peça do seu projeto:

```text
aula-quinze-de-maio/internet_banking_tests/
│
├── app.py                     # 💻 O código principal do nosso Internet Banking.
├── config.py                  # ⚙️ Configurações gerais (onde o banco de dados fica salvo).
├── banking.db                 # 🗄️ O arquivo do banco de dados SQLite onde guardamos saldos e contas.
│
├── conftest.py                # 🛠️ Reinicia o banco de dados limpo antes de cada teste.
├── pytest.ini                 # 📝 Configura o Pytest para executar os testes BDD.
├── setup.cfg                  # ⚙️ Configura o Mutmut para não testar arquivos desnecessários.
│
├── test_transferencia.py      # 🐍 Liga as historinhas do Gherkin ao código Python de testes.
├── features/                  # 📚 Pasta contendo os comportamentos em português estruturado.
│   └── transferencia.feature  # 💬 As historinhas escritas em Gherkin (Dado, Quando, Então).
│
├── relatorios/                # 📂 ARQUIVOS PARA VOCÊ ENVIAR NO AVA:
│   ├── Relatorio_Sprint4_LeonardoEliel.docx   # Documento Word formatado da Sprint 4.
│   ├── Relatorio_Sprint5_LeonardoEliel.docx   # Documento Word formatado da Sprint 5.
│   └── Relatorio_Sprint6_LeonardoEliel.docx   # Documento Word formatado da Sprint 6.
│   ├── ... (outros arquivos de texto simplificados da sua jornada)
│
├── backups/                   # 🗃️ Cópias antigas do seu código e rascunhos para segurança.
├── legacy/                    # ⏳ Testes antigos desativados (Hypothesis, etc).
└── venv/                      # 📦 A biblioteca virtual com as dependências do Python.
```

---

## 💡 Resumo do Aprendizado
Nós aprendemos que ter **100% de cobertura de código** (passar por todas as linhas) não significa que o software está livre de erros. Se os testes forem superficiais, os erros passam. 

Ao unir o **BDD** (que garante que estamos fazendo o que o cliente pediu) com os **Testes de Mutação** (que desafiam as defesas dos nossos testes inserindo bugs propositais), garantimos que o sistema seja seguro, robusto e livre de surpresas desagradáveis.
