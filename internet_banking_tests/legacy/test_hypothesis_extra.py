# Leonardo Eliel Dias da Silva - Pt-br - UTF-8
# test_hypothesis_extra.py
import requests
import pytest
from hypothesis import given, strategies as st, assume, settings

BASE_URL = "http://127.0.0.1:5000"

# Invariante Extra 1: Para qualquer conta ID ∈ {1, 2, 3}, tentar realizar uma transferência onde a conta
# de origem é igual à conta de destino deve sempre retornar HTTP 422.
@given(
    conta_id=st.sampled_from([1, 2, 3]),
    valor=st.floats(min_value=0.01, max_value=1000.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=30)
def test_invariante_extra1_mesma_conta(conta_id, valor):
    response = requests.post(
        f"{BASE_URL}/transferencia",
        json={"origem": conta_id, "destino": conta_id, "valor": float(valor)}
    )
    assert response.status_code == 422
    assert response.json()["erro"] == "Origem e destino nao podem ser iguais"


# Invariante Extra 2: Para qualquer ID inteiro fora do conjunto {1, 2, 3}, o endpoint /extrato/<conta_id>
# deve sempre retornar HTTP 404.
@given(
    conta_id=st.integers().filter(lambda x: x not in (1, 2, 3))
)
@settings(max_examples=30)
def test_invariante_extra2_extrato_inexistente(conta_id):
    response = requests.get(f"{BASE_URL}/extrato/{conta_id}")
    assert response.status_code == 404
    
    # Se o ID for negativo, o Flask não casa a rota /extrato/<int:conta_id>
    # e retorna uma página HTML 404 genérica. Se for positivo, retorna JSON.
    if "application/json" in response.headers.get("Content-Type", ""):
        assert response.json()["erro"] == "Conta nao encontrada"
