"""
Testes para T-001 — Fundação, CLI e conversor de valores em centavos.
Atende: RN-010, RN-014, AMB-008, AMB-013
"""
import json
import pytest
from src.parser import float_to_cents, parse_input_file


def test_float_to_cents_conversion():
    """Valida conversão de float para inteiros em centavos usando arredondamento half-up."""
    assert float_to_cents(72.50) == 7250
    assert float_to_cents(38.00) == 3800
    assert float_to_cents(33.333) == 3333
    assert float_to_cents(100.01) == 10001
    assert float_to_cents(-45.00) == -4500
    assert float_to_cents(0.0) == 0


def test_cli_parse_input_to_cents(tmp_path):
    """Testa leitura de arquivo JSON válido e conversão das despesas em centavos."""
    sample_data = {
        "colaborador": {
            "id": "c-0417",
            "nome": "Marina Volpi",
            "centro_custo": "CC-ENG-PLATAFORMA"
        },
        "periodo": {
            "competencia": "2026-07",
            "inicio": "2026-07-01",
            "fim": "2026-07-31"
        },
        "despesas": [
            {
                "id": "d-001",
                "data": "2026-07-03",
                "categoria": "alimentacao",
                "descricao": "Almoco com cliente",
                "fornecedor": "Restaurante Tavola",
                "valor": 72.50,
                "tem_nota_fiscal": True
            }
        ]
    }
    input_file = tmp_path / "input.json"
    input_file.write_text(json.dumps(sample_data), encoding="utf-8")

    colaborador, periodo, despesas = parse_input_file(str(input_file))

    assert colaborador.id == "c-0417"
    assert periodo.competencia == "2026-07"
    assert len(despesas) == 1
    assert despesas[0].id == "d-001"
    assert despesas[0].valor_centavos == 7250


def test_parse_input_file_not_found():
    """Valida erro ao tentar abrir arquivo inexistente."""
    with pytest.raises(FileNotFoundError):
        parse_input_file("arquivo_inexistente_12345.json")


def test_parse_input_invalid_json(tmp_path):
    """Valida erro ao ler JSON corrompido."""
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{ json_invalido ", encoding="utf-8")
    with pytest.raises(ValueError):
        parse_input_file(str(bad_file))
