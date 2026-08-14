"""
Testes para T-011 — Execução da CLI (`calcular --input despesas.json --output resultado.json`).
Atende: Seção 2.5 de DESAFIO.md
"""
import json
import os
import subprocess
import pytest


def test_cli_execucao_comando(tmp_path):
    """Executa a CLI via subprocesso e verifica o arquivo de saída gerado."""
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
