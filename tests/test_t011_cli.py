"""
Testes para T-011 / T-017 — Execução da CLI (`calcular --input despesas.json --output resultado.json`).
Atende: Seção 2.5 de DESAFIO.md e CLI v2.0
"""
import json
import os
import subprocess


def test_cli_execucao_comando(tmp_path):
    """Executa a CLI padrão via subprocesso e verifica o arquivo de saída gerado."""
    input_file = os.path.join("exemplos", "despesas-exemplo.json")
    output_file = str(tmp_path / "resultado.json")

    cmd = [
        "python", "-m", "src.cli", "calcular",
        "--input", input_file,
        "--output", output_file
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0
    assert os.path.exists(output_file)

    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "colaborador" in data
    assert "resumo" in data
    assert "itens" in data
    assert len(data["itens"]) == 14


def test_cli_execucao_envelope_v4(tmp_path):
    """Executa a CLI v2.0 informando --politica e --cambio para o envelope."""
    input_file = os.path.join("exemplos", "envelope", "despesas-envelope.json")
    pol_file = os.path.join("exemplos", "envelope", "politica-v4.json")
    cam_file = os.path.join("exemplos", "envelope", "cambio.json")
    output_file = str(tmp_path / "resultado_env.json")

    cmd = [
        "python", "-m", "src.cli", "calcular",
        "--input", input_file,
        "--output", output_file,
        "--politica", pol_file,
        "--cambio", cam_file
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0
    assert os.path.exists(output_file)

    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["colaborador"]["centro_custo"] == "CC-COMERCIAL"
    assert len(data["itens"]) == 10
