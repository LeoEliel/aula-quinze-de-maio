# test_transferencia.py
# Sprint 5 — Execução dos cenários BDD

import sqlite3
import pytest
from pathlib import Path
from pytest_bdd import given, when, then, parsers, scenarios

# Resolve caminhos para funcionar com pytest e mutmut
_PROJECT_ROOT = Path(__file__).resolve().parent
if _PROJECT_ROOT.name == "mutants":
    _PROJECT_ROOT = _PROJECT_ROOT.parent

_FEATURES = str(_PROJECT_ROOT / "features")
_DB_PATH  = str(_PROJECT_ROOT / "banking.db")

# Carrega os cenários definidos no arquivo feature
scenarios(f"{_FEATURES}/transferencia.feature")

@pytest.fixture
def client():
    """Fornece o client de teste do Flask, sem usar requests (rede)."""
    from app import app
    app.config["DATABASE"] = _DB_PATH
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c

@pytest.fixture
def context():
    """Dicionário para compartilhar dados (como a resposta) entre os passos."""
    return {}

# --- DADO ---

@given(parsers.parse("a conta {conta_id:d} tem saldo de {saldo:f}"), target_fixture="context")
def dado_conta_com_saldo(conta_id, saldo):
    conn = sqlite3.connect(_DB_PATH)
    conn.execute("UPDATE contas SET saldo = ? WHERE id = ?", (saldo, conta_id))
    conn.commit()
    conn.close()
    return {}

@given(parsers.parse("a conta {c2:d} tem saldo de {s2:f}"), target_fixture="context")
def dado_conta_adicional_com_saldo(c2, s2, context):
    conn = sqlite3.connect(_DB_PATH)
    conn.execute("UPDATE contas SET saldo = ? WHERE id = ?", (s2, c2))
    conn.commit()
    conn.close()
    return context

@given("o sistema esta inicializado", target_fixture="context")
def dado_sistema_inicializado():
    # O conftest.py já inicializa e reseta o banco de dados antes de cada teste.
    return {}

# --- QUANDO ---

@when(parsers.parse("o cliente transfere {valor:f} da conta {origem:d} para a conta {destino:d}"), target_fixture="context")
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

# --- ENTÃO ---

@then(parsers.parse("a resposta deve ter status {status:d}"))
def entao_status(context, status):
    resp = context["response"]
    assert resp.status_code == status, f"Esperado {status}, obtido {resp.status_code}"

@then(parsers.parse('a mensagem de retorno deve ser "{mensagem}"'))
def entao_mensagem_sucesso(context, mensagem):
    data = context["response"].get_json()
    assert data["mensagem"] == mensagem

@then(parsers.parse('a mensagem de erro deve ser "{mensagem}"'))
def entao_mensagem_erro(context, mensagem):
    data = context["response"].get_json()
    assert data["erro"] == mensagem

@then(parsers.parse("o saldo da conta {conta_id:d} deve ser {saldo_esperado:f}"))
def entao_saldo_conta(client, conta_id, saldo_esperado):
    resp = client.get(f"/saldo/{conta_id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert abs(data["saldo"] - saldo_esperado) < 1e-5, f"Saldo incorreto: {data['saldo']}"
