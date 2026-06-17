# conftest.py — Sprint 5
# Prepara o ambiente para o pytest e para o mutmut.
#
# O mutmut copia apenas o app.py para a pasta mutants/ antes de cada execução.
# O config.py fica no diretório pai. Por isso, precisamos:
#   1. Adicionar o diretório pai ao sys.path para que `import config` funcione.
#   2. Resetar o banco antes de cada teste (isolamento).

import sys
import os
import pytest
import sqlite3
from pathlib import Path

# Garante que o diretório raiz do projeto esteja no sys.path,
# mesmo quando o pytest é executado de dentro de mutants/.
_ROOT = Path(__file__).resolve().parent
if _ROOT.name == "mutants":
    _ROOT = _ROOT.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
if str(_ROOT.parent) not in sys.path:
    sys.path.insert(0, str(_ROOT.parent))

# Também adiciona o diretório atual de trabalho, para compatibilidade.
_CWD = Path(os.getcwd()).resolve()
if str(_CWD) not in sys.path:
    sys.path.insert(0, str(_CWD))
if str(_CWD.parent) not in sys.path:
    sys.path.insert(0, str(_CWD.parent))

# Caminho absoluto do banco SQLite — funciona independente do CWD.
_DB_PATH = str(_ROOT / "banking.db")


@pytest.fixture(autouse=True)
def reset_banco():
    """Restaura o banco para o estado canônico antes de cada teste."""
    conn = sqlite3.connect(_DB_PATH)
    conn.execute("UPDATE contas SET saldo = 1000.00 WHERE id = 1")
    conn.execute("UPDATE contas SET saldo =  500.00 WHERE id = 2")
    conn.execute("UPDATE contas SET saldo =    0.00 WHERE id = 3")
    conn.execute("DELETE FROM transferencias")
    conn.commit()
    conn.close()
    yield
