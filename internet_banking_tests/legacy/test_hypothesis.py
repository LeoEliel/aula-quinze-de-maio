# Leonardo Eliel Dias da Silva - Pt-br - UTF-8
# test_hypothesis.py
import requests
import pytest
from hypothesis import given, strategies as st, assume, settings

BASE_URL = "http://127.0.0.1:5000"

# Invariante 1: para qualquer valor não-positivo (zero ou negativo) submetido ao endpoint /transferencia,
# o sistema deve sempre retornar HTTP 422 - valor inválido.
@given(
    origem=st.sampled_from([1, 2, 3]),
    destino=st.sampled_from([1, 2, 3]),
    valor=st.floats(max_value=0.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=30)
def test_invariante1_valor_nao_positivo(origem, destino, valor):
    assume(origem != destino)
    response = requests.post(
        f"{BASE_URL}/transferencia",
        json={"origem": origem, "destino": destino, "valor": float(valor)}
    )
    assert response.status_code == 422
    assert response.json()["erro"] == "Valor deve ser positivo"


# Invariante 2: para qualquer ID inteiro que não pertença ao conjunto de contas cadastradas no sistema
# (ou seja, ID fora do conjunto {1, 2, 3}), o endpoint /saldo/<conta_id> deve sempre retornar HTTP 404 - conta não encontrada.
@given(
    conta_id=st.integers().filter(lambda x: x not in (1, 2, 3))
)
@settings(max_examples=30)
def test_invariante2_conta_inexistente(conta_id):
    response = requests.get(f"{BASE_URL}/saldo/{conta_id}")
    assert response.status_code == 404
    
    # Se o ID for negativo, o Flask não casa a rota /saldo/<int:conta_id> (pois int só aceita positivos >= 0).
    # Assim, ele retorna uma página HTML 404 genérica do Flask. Se for positivo, retorna JSON.
    if "application/json" in response.headers.get("Content-Type", ""):
        assert response.json()["erro"] == "Conta nao encontrada"


# Invariante 3: para qualquer transferência aceita pelo endpoint /transferencia (resposta HTTP 200),
# a soma dos saldos das contas de origem e destino imediatamente após a operação deve ser exatamente
# igual à soma dos saldos imediatamente antes da operação.
@given(
    origem=st.sampled_from([1, 2, 3]),
    destino=st.sampled_from([1, 2, 3]),
    valor=st.floats(min_value=0.01, max_value=2000.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=30)
def test_invariante3_conservacao_saldos(origem, destino, valor):
    assume(origem != destino)
    
    # Obter saldos antes
    resp_origem_antes = requests.get(f"{BASE_URL}/saldo/{origem}")
    resp_destino_antes = requests.get(f"{BASE_URL}/saldo/{destino}")
    assume(resp_origem_antes.status_code == 200)
    assume(resp_destino_antes.status_code == 200)
    
    saldo_origem_antes = resp_origem_antes.json()["saldo"]
    saldo_destino_antes = resp_destino_antes.json()["saldo"]
    
    # Realizar transferência
    response = requests.post(
        f"{BASE_URL}/transferencia",
        json={"origem": origem, "destino": destino, "valor": float(valor)}
    )
    
    # Se a transferência foi aceita, verificar conservação
    if response.status_code == 200:
        resp_origem_depois = requests.get(f"{BASE_URL}/saldo/{origem}")
        resp_destino_depois = requests.get(f"{BASE_URL}/saldo/{destino}")
        
        assert resp_origem_depois.status_code == 200
        assert resp_destino_depois.status_code == 200
        
        saldo_origem_depois = resp_origem_depois.json()["saldo"]
        saldo_destino_depois = resp_destino_depois.json()["saldo"]
        
        soma_antes = saldo_origem_antes + saldo_destino_antes
        soma_depois = saldo_origem_depois + saldo_destino_depois
        
        # Comparação com tolerância para ponto flutuante
        assert abs(soma_antes - soma_depois) < 1e-5
