# Matriz de Rastreabilidade — ISO/IEC/IEEE 29119-3
**Gerada automaticamente em:** 2026-06-23 23:22:39
**Total de testes no report.xml:** 8
**Casos especificados no caderno 29119-3:** 4

## Rastreabilidade: Requisito ↔ Caso de Teste ↔ Evidência

| ID Caso | Sprint | Requisito | Nível BSTQB | Técnica | Área TMMi | Status | Tempo |
|---------|--------|-----------|-------------|---------|-----------|--------|-------|
| TC-S1-001 | Sprint 1 | REQ-TRANS-001: Transferência com saldo >... | Componente | Caixa-Preta — Análise de Valor... | Test Design and Execution... | ⚠ SEM EVIDÊNCIA | N/A |
| TC-S3-001 | Sprint 3 | REQ-TRANS-002: Valor deve ser estritamen... | Sistema | Caixa-Preta — Baseada em Propr... | Test Design and Execution... | ⚠ SEM EVIDÊNCIA | N/A |
| TC-S4-001 | Sprint 4 | REQ-TRANS-003: Débito e crédito consiste... | Integração | Caixa-Branca — Cobertura de In... | Test Environment... | ✅ PASSOU | 0.030s |
| TC-S5-001 | Sprint 5 | REQ-TRANS-004: Origem e destino devem se... | Aceitação (UAT) | Caixa-Preta — BDD/Gherkin (Tes... | Test Design and Execution... | ✅ PASSOU | 0.018s |

## Resumo
- ✅ Casos com evidência positiva: **2**
- ❌ Casos com falha: **0**
- ⚠ Casos sem evidência no pipeline: **2**

## Detalhamento dos Casos Especificados

### TC-S1-001 — Transferência com saldo exatamente igual ao valor (borda crítica)
- **Artefato de origem:** `legacy/test_ia_gerado.py`
- **Sprint:** Sprint 1
- **Nível BSTQB:** Componente
- **Técnica BSTQB:** Caixa-Preta — Análise de Valor Limite
- **Área TMMi:** Test Design and Execution
- **Requisito rastreado:** REQ-TRANS-001: Transferência com saldo >= valor deve ser aceita
- **Resultado:** ⚠ Sem evidência no report.xml (teste legado ou nome divergente)

### TC-S3-001 — Invariante: qualquer valor não-positivo retorna HTTP 422
- **Artefato de origem:** `legacy/test_hypothesis.py`
- **Sprint:** Sprint 3
- **Nível BSTQB:** Sistema
- **Técnica BSTQB:** Caixa-Preta — Baseada em Propriedade (Hypothesis)
- **Área TMMi:** Test Design and Execution
- **Requisito rastreado:** REQ-TRANS-002: Valor deve ser estritamente positivo
- **Resultado:** ⚠ Sem evidência no report.xml (teste legado ou nome divergente)

### TC-S4-001 — Transferência válida débita origem e credita destino (BDD refatorado)
- **Artefato de origem:** `test_transferencia.py`
- **Sprint:** Sprint 4
- **Nível BSTQB:** Integração
- **Técnica BSTQB:** Caixa-Branca — Cobertura de Instruções (refatorado para test_client)
- **Área TMMi:** Test Environment
- **Requisito rastreado:** REQ-TRANS-003: Débito e crédito consistentes entre contas
- **Resultado:** ✅ PASSOU (0.030s)

### TC-S5-001 — Cenário BDD: transferência da conta para ela mesma é bloqueada
- **Artefato de origem:** `features/transferencia.feature`
- **Sprint:** Sprint 5
- **Nível BSTQB:** Aceitação (UAT)
- **Técnica BSTQB:** Caixa-Preta — BDD/Gherkin (Teste de Aceite)
- **Área TMMi:** Test Design and Execution
- **Requisito rastreado:** REQ-TRANS-004: Origem e destino devem ser diferentes
- **Resultado:** ✅ PASSOU (0.018s)

## Todos os testes executados no pipeline

| # | Teste | Classe | Status | Tempo |
|---|-------|--------|--------|-------|
| 1 | test_transferencia_com_conta_de_origem_inexistente | test_transferencia | ✅ PASSOU | 0.016s |
| 2 | test_transferencia_com_saldo_exatamente_igual_ao_v | test_transferencia | ✅ PASSOU | 0.856s |
| 3 | test_transferencia_com_saldo_insuficiente_deve_ser | test_transferencia | ✅ PASSOU | 0.020s |
| 4 | test_transferencia_com_valor_negativo_deve_ser_rej | test_transferencia | ✅ PASSOU | 0.015s |
| 5 | test_transferencia_com_valor_zero_deve_ser_rejeita | test_transferencia | ✅ PASSOU | 0.014s |
| 6 | test_transferencia_da_conta_para_ela_mesma_deve_se | test_transferencia | ✅ PASSOU | 0.018s |
| 7 | test_transferencia_sem_campos_obrigatorios_retorna | test_transferencia | ✅ PASSOU | 0.016s |
| 8 | test_transferencia_valida_debita_origem_e_credita_ | test_transferencia | ✅ PASSOU | 0.030s |

---
*Relatório gerado por `scripts/gera_matriz.py` — Sprint 8 ISO/IEC/IEEE 29119-3*
