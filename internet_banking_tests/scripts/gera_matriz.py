#!/usr/bin/env python3
# scripts/gera_matriz.py
# Sprint 8 — Geração automática da Matriz de Rastreabilidade
# Requisito ↔ Caso de Teste ↔ Evidência de Execução
#
# Lê o report.xml (JUnit XML) gerado pelo pytest e cruza com os IDs
# de teste especificados no caderno ISO/IEC/IEEE 29119-3.
# Saída: tabela Markdown para uso como artefato do pipeline CI.
#
# Leonardo Eliel Dias da Silva — IFRO Campus Ariquemes

import xml.etree.ElementTree as ET
import os
import sys
from datetime import datetime

# ============================================================
# MAPEAMENTO: Caderno 29119-3 → Requisito → Caso de Teste
# ============================================================
CADERNO_29119 = [
    {
        "id_caso": "TC-S1-001",
        "descricao": "Transferência com saldo exatamente igual ao valor (borda crítica)",
        "artefato_origem": "legacy/test_ia_gerado.py",
        "sprint": "Sprint 1",
        "nivel_bstqb": "Componente",
        "tecnica_bstqb": "Caixa-Preta — Análise de Valor Limite",
        "area_tmmi": "Test Design and Execution",
        "requisito": "REQ-TRANS-001: Transferência com saldo >= valor deve ser aceita",
        "funcao_pytest": "test_transferencia_saldo_igual_valor",
    },
    {
        "id_caso": "TC-S3-001",
        "descricao": "Invariante: qualquer valor não-positivo retorna HTTP 422",
        "artefato_origem": "legacy/test_hypothesis.py",
        "sprint": "Sprint 3",
        "nivel_bstqb": "Sistema",
        "tecnica_bstqb": "Caixa-Preta — Baseada em Propriedade (Hypothesis)",
        "area_tmmi": "Test Design and Execution",
        "requisito": "REQ-TRANS-002: Valor deve ser estritamente positivo",
        "funcao_pytest": "test_invariante1_valor_nao_positivo",
    },
    {
        "id_caso": "TC-S4-001",
        "descricao": "Transferência válida débita origem e credita destino (BDD refatorado)",
        "artefato_origem": "test_transferencia.py",
        "sprint": "Sprint 4",
        "nivel_bstqb": "Integração",
        "tecnica_bstqb": "Caixa-Branca — Cobertura de Instruções (refatorado para test_client)",
        "area_tmmi": "Test Environment",
        "requisito": "REQ-TRANS-003: Débito e crédito consistentes entre contas",
        "funcao_pytest": "test_transferencia_valida_debita_origem_e_credita_destino_corretamente",
    },
    {
        "id_caso": "TC-S5-001",
        "descricao": "Cenário BDD: transferência da conta para ela mesma é bloqueada",
        "artefato_origem": "features/transferencia.feature",
        "sprint": "Sprint 5",
        "nivel_bstqb": "Aceitação (UAT)",
        "tecnica_bstqb": "Caixa-Preta — BDD/Gherkin (Teste de Aceite)",
        "area_tmmi": "Test Design and Execution",
        "requisito": "REQ-TRANS-004: Origem e destino devem ser diferentes",
        "funcao_pytest": "test_transferencia_da_conta_para_ela_mesma_deve_ser_bloqueada",
    },
]


def parse_junit_xml(report_path):
    """Lê o report.xml e retorna dict {nome_teste: (status, tempo, mensagem)}."""
    resultados = {}
    if not os.path.exists(report_path):
        print(f"⚠ Arquivo {report_path} não encontrado.", file=sys.stderr)
        return resultados

    tree = ET.parse(report_path)
    root = tree.getroot()

    for testsuite in root.iter("testsuite"):
        for testcase in testsuite.iter("testcase"):
            nome = testcase.get("name", "desconhecido")
            classname = testcase.get("classname", "")
            tempo = testcase.get("time", "0")

            failure = testcase.find("failure")
            error = testcase.find("error")
            skipped = testcase.find("skipped")

            if failure is not None:
                status = "❌ FALHOU"
                msg = failure.get("message", "sem mensagem")
            elif error is not None:
                status = "💥 ERRO"
                msg = error.get("message", "sem mensagem")
            elif skipped is not None:
                status = "⏭ PULADO"
                msg = skipped.get("message", "sem mensagem")
            else:
                status = "✅ PASSOU"
                msg = ""

            # Usar nome completo para matching
            chave = nome.lower().replace(" ", "_").replace("-", "_")
            resultados[chave] = {
                "status": status,
                "tempo": tempo,
                "mensagem": msg,
                "classname": classname,
                "nome_original": nome,
            }

    return resultados


def encontrar_evidencia(caso, resultados):
    """Tenta encontrar o resultado do caso de teste no report.xml."""
    funcao = caso["funcao_pytest"].lower().replace("-", "_")

    # Busca exata
    if funcao in resultados:
        return resultados[funcao]

    # Busca parcial (nome contido)
    for chave, valor in resultados.items():
        if funcao in chave or chave in funcao:
            return valor

    # Busca pelo nome original
    for chave, valor in resultados.items():
        nome_original = valor["nome_original"].lower().replace(" ", "_").replace("-", "_")
        if funcao in nome_original or nome_original in funcao:
            return valor

    return None


def gerar_matriz(report_path="report.xml"):
    """Gera a matriz de rastreabilidade em Markdown."""
    resultados = parse_junit_xml(report_path)
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    linhas = []
    linhas.append("# Matriz de Rastreabilidade — ISO/IEC/IEEE 29119-3")
    linhas.append(f"**Gerada automaticamente em:** {agora}")
    linhas.append(f"**Total de testes no report.xml:** {len(resultados)}")
    linhas.append(f"**Casos especificados no caderno 29119-3:** {len(CADERNO_29119)}")
    linhas.append("")
    linhas.append("## Rastreabilidade: Requisito ↔ Caso de Teste ↔ Evidência")
    linhas.append("")

    # Cabeçalho da tabela
    linhas.append(
        "| ID Caso | Sprint | Requisito | Nível BSTQB | Técnica | Área TMMi | Status | Tempo |"
    )
    linhas.append(
        "|---------|--------|-----------|-------------|---------|-----------|--------|-------|"
    )

    total_pass = 0
    total_fail = 0
    total_norun = 0

    for caso in CADERNO_29119:
        evidencia = encontrar_evidencia(caso, resultados)
        if evidencia:
            status = evidencia["status"]
            tempo = f"{float(evidencia['tempo']):.3f}s"
            if "PASSOU" in status:
                total_pass += 1
            else:
                total_fail += 1
        else:
            status = "⚠ SEM EVIDÊNCIA"
            tempo = "N/A"
            total_norun += 1

        linhas.append(
            f"| {caso['id_caso']} | {caso['sprint']} | {caso['requisito'][:40]}... "
            f"| {caso['nivel_bstqb']} | {caso['tecnica_bstqb'][:30]}... "
            f"| {caso['area_tmmi'][:25]}... | {status} | {tempo} |"
        )

    linhas.append("")
    linhas.append("## Resumo")
    linhas.append(f"- ✅ Casos com evidência positiva: **{total_pass}**")
    linhas.append(f"- ❌ Casos com falha: **{total_fail}**")
    linhas.append(f"- ⚠ Casos sem evidência no pipeline: **{total_norun}**")
    linhas.append("")

    # Detalhamento dos casos
    linhas.append("## Detalhamento dos Casos Especificados")
    linhas.append("")

    for caso in CADERNO_29119:
        evidencia = encontrar_evidencia(caso, resultados)
        linhas.append(f"### {caso['id_caso']} — {caso['descricao']}")
        linhas.append(f"- **Artefato de origem:** `{caso['artefato_origem']}`")
        linhas.append(f"- **Sprint:** {caso['sprint']}")
        linhas.append(f"- **Nível BSTQB:** {caso['nivel_bstqb']}")
        linhas.append(f"- **Técnica BSTQB:** {caso['tecnica_bstqb']}")
        linhas.append(f"- **Área TMMi:** {caso['area_tmmi']}")
        linhas.append(f"- **Requisito rastreado:** {caso['requisito']}")
        if evidencia:
            linhas.append(f"- **Resultado:** {evidencia['status']} ({float(evidencia['tempo']):.3f}s)")
            if evidencia["mensagem"]:
                linhas.append(f"- **Mensagem:** {evidencia['mensagem'][:100]}")
        else:
            linhas.append("- **Resultado:** ⚠ Sem evidência no report.xml (teste legado ou nome divergente)")
        linhas.append("")

    # Todos os testes executados no pipeline
    linhas.append("## Todos os testes executados no pipeline")
    linhas.append("")
    linhas.append("| # | Teste | Classe | Status | Tempo |")
    linhas.append("|---|-------|--------|--------|-------|")
    for i, (chave, valor) in enumerate(sorted(resultados.items()), 1):
        linhas.append(
            f"| {i} | {valor['nome_original'][:50]} | {valor['classname'][:30]} "
            f"| {valor['status']} | {float(valor['tempo']):.3f}s |"
        )

    linhas.append("")
    linhas.append("---")
    linhas.append(f"*Relatório gerado por `scripts/gera_matriz.py` — Sprint 8 ISO/IEC/IEEE 29119-3*")

    return "\n".join(linhas)


if __name__ == "__main__":
    report_path = sys.argv[1] if len(sys.argv) > 1 else "report.xml"
    print(gerar_matriz(report_path))
