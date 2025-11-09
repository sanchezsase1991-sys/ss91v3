import pytest
from ss91_v3.data_pipeline import ejecutar_busqueda_avanzada

def test_fetch_basic():
    res = ejecutar_busqueda_avanzada("sentimiento EURUSD")
    assert isinstance(res, dict)
    assert 'value' in res and 'confidence' in res

