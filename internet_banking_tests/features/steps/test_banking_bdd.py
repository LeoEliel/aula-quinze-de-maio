# features/steps/test_banking_bdd.py
# Sprint 5 — Testes BDD com pytest-bdd
# Leonardo Eliel Dias da Silva
#
# Arquivo nomeado test_*.py para que o pytest o colete automaticamente.
# Os cenários Gherkin ficam em features/*.feature e são carregados via scenarios().

import pytest
import sqlite3
from pytest_bdd import given, when, then, parsers, scenarios

# Carrega todos os cenários dos dois feature files
scenarios("../transferencia.feature")
scenarios("../saldo_extrato.feature")


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def client():
    """Flask test client — substitui requests HTTP. Compatível com mutmut."""
    from app import app, init_db
    app.config["DATABASE"] = "banking.db"
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture
def context():
    """Dicionário compartilhado para passar dados entre steps."""
    return {}


# ============================================================
# STEPS — GIVEN
# ============================================================

@given(parsers.parse("a conta {conta_id:d} tem saldo de {saldo:f}"), target_fixture="context")
def dado_conta_com_saldo(conta_id, saldo):
    conn = sqlite3.connect("banking.db")
    conn.execute("UPDATE contas SET saldo = ? WHERE id = ?", (saldo, conta_id))
    conn.commit()
    conn.close()
    return {}


@given(parsers.parse("a conta {c2:d} tem saldo de {s2:f}"), target_fixture="context")
def dado_conta_adicional_com_saldo(c2, s2, context):
    conn = sqlite3.connect("banking.db")
    conn.execute("UPDATE contas SET saldo = ? WHERE id = ?", (s2, c2))
    conn.commit()
    conn.close()
    return context


@given("o sistema esta inicializado", target_fixture="context")
def dado_sistema_inicializado():
    return {}


# ============================================================
# STEPS — WHEN
# ============================================================

@when(
    parsers.parse("o cliente transfere {valor:f} da conta {origem:d} para a conta {destino:d}"),
    target_fixture="context"
)
def quando_transfere(client, context, valor, origem, destino):
    resp = client.post(
        "/transferencia",
        json={"origem": origem, "destino": destino, "valor": valor}
    )
    context["response"] = resp
    return context


@when("o cliente envia uma transferencia sem o campo valor", target_fixture="context")
def quando_transfere_sem_valor(client, context):
    resp = client.post("/transferencia", json={"origem": 1, "destino": 2})
    context["response"] = resp
    return context


@when(parsers.parse("o cliente consulta o saldo da conta {conta_id:d}"), target_fixture="context")
def quando_consulta_saldo(client, context, conta_id):
    resp = client.get(f"/saldo/{conta_id}")
    context["response"] = resp
    return context


@when(parsers.parse("o cliente consulta o extrato da conta {conta_id:d}"), target_fixture="context")
def quando_consulta_extrato(client, context, conta_id):
    resp = client.get(f"/extrato/{conta_id}")
    context["response"] = resp
    return context


# ============================================================
# STEPS — THEN
# ============================================================

@then(parsers.parse("a resposta deve ter status {status:d}"))
def entao_status(context, status):
    resp = context["response"]
    assert resp.status_code == status, (
        f"Esperado status {status}, obtido {resp.status_code}. "
        f"Body: {resp.get_data(as_text=True)}"
    )


@then(parsers.parse('a mensagem de retorno deve ser "{mensagem}"'))
def entao_mensagem_sucesso(context, mensagem):
    data = context["response"].get_json()
    assert data["mensagem"] == mensagem, (
        f"Esperado '{mensagem}', obtido '{data.get('mensagem')}'"
    )


@then(parsers.parse('a mensagem de erro deve ser "{mensagem}"'))
def entao_mensagem_erro(context, mensagem):
    data = context["response"].get_json()
    assert data["erro"] == mensagem, (
        f"Esperado erro '{mensagem}', obtido '{data.get('erro')}'"
    )


@then(parsers.parse("o saldo da conta {conta_id:d} deve ser {saldo_esperado:f}"))
def entao_saldo_conta(client, conta_id, saldo_esperado):
    resp = client.get(f"/saldo/{conta_id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert abs(data["saldo"] - saldo_esperado) < 1e-5, (
        f"Conta {conta_id}: esperado {saldo_esperado}, obtido {data['saldo']}"
    )


@then(parsers.parse('o campo "{campo}" deve ser {valor:d}'))
def entao_campo_inteiro(context, campo, valor):
    data = context["response"].get_json()
    assert data[campo] == valor, (
        f"Campo '{campo}': esperado {valor}, obtido {data.get(campo)}"
    )


@then(parsers.parse('o campo "{campo}" deve ser "{valor}"'))
def entao_campo_texto(context, campo, valor):
    data = context["response"].get_json()
    assert data[campo] == valor, (
        f"Campo '{campo}': esperado '{valor}', obtido '{data.get(campo)}'"
    )


@then(parsers.parse('o campo "{campo}" deve estar presente'))
def entao_campo_presente(context, campo):
    data = context["response"].get_json()
    assert campo in data, (
        f"Campo '{campo}' não encontrado. Campos: {list(data.keys())}"
    )
