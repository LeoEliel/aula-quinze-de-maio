# Leonardo Eliel Dias da Silva - Pt-br - UTF-8
# test_ia_gerado.py

import requests

BASE_URL = "http://127.0.0.1:5000"

# ENDPOINT: GET /saldo/<conta_id>
def test_saldo_conta_existente():
    response = requests.get(f"{BASE_URL}/saldo/1")
    assert response.status_code == 200
    data = response.json()
    assert data["conta_id"] == 1
    assert data["titular"] == "Alice"
    assert "saldo" in data

def test_saldo_conta_inexistente():
    response = requests.get(f"{BASE_URL}/saldo/999")
    assert response.status_code == 404
    assert response.json()["erro"] == "Conta nao encontrada"

# ENDPOINT: POST /transferencia
def test_transferencia_valida():
    response = requests.post(
        f"{BASE_URL}/transferencia",
        json={"origem": 2, "destino": 3, "valor": 100.0}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["mensagem"] == "Transferencia realizada"
    assert data["valor"] == 100.0

# Primeiro teste TDD
def test_transferencia_saldo_igual_valor():
    response = requests.post(
        f"{BASE_URL}/transferencia",
        json={"origem": 1, "destino": 2, "valor": 1000.0}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["mensagem"] == "Transferencia realizada"
    assert data["valor"] == 1000.0

def test_transferencia_saldo_insuficiente():
    response = requests.post(
        f"{BASE_URL}/transferencia",
        json={"origem": 1, "destino": 2, "valor": 9999.0}
    )
    assert response.status_code == 422
    assert response.json()["erro"] == "Saldo insuficiente"

def test_transferencia_valor_negativo():
    response = requests.post(
        f"{BASE_URL}/transferencia",
        json={"origem": 1, "destino": 2, "valor": -50.0}
    )
    assert response.status_code == 422
    assert response.json()["erro"] == "Valor deve ser positivo"

def test_transferencia_valor_zero():
    response = requests.post(
        f"{BASE_URL}/transferencia",
        json={"origem": 1, "destino": 2, "valor": 0.0}
    )
    assert response.status_code == 422
    assert response.json()["erro"] == "Valor deve ser positivo"

def test_transferencia_campos_ausentes():
    response = requests.post(
        f"{BASE_URL}/transferencia",
        json={"origem": 1}
    )
    assert response.status_code == 400
    assert response.json()["erro"] == "Campos obrigatorios ausentes: origem, destino, valor"

def test_transferencia_conta_origem_inexistente():
    response = requests.post(
        f"{BASE_URL}/transferencia",
        json={"origem": 999, "destino": 2, "valor": 100.0}
    )
    assert response.status_code == 404
    assert response.json()["erro"] == "Conta nao encontrada"

def test_transferencia_mesma_conta():
    response = requests.post(
        f"{BASE_URL}/transferencia",
        json={"origem": 1, "destino": 1, "valor": 100.0}
    )
    assert response.status_code == 422
    assert response.json()["erro"] == "Origem e destino nao podem ser iguais"

# ENDPOINT: GET /extrato/<conta_id>
def test_extrato_conta_existente():
    response = requests.get(f"{BASE_URL}/extrato/1")
    assert response.status_code == 200
    data = response.json()
    assert data["conta_id"] == 1
    assert "historico" in data
    assert "saldo_atual" in data

def test_extrato_conta_inexistente():
    response = requests.get(f"{BASE_URL}/extrato/999")
    assert response.status_code == 404
    assert response.json()["erro"] == "Conta nao encontrada"
