"""
Interface de Linha de Comando (CLI) para a execução do motor de reembolso.
Interface esperada: python -m src.cli calcular --input despesas.json --output resultado.json
"""
import sys
import argparse
from src.parser import parse_input_file
from src.engine import processar_relatorio_despesas
from src.formatter import construir_relatorio_saida, salvar_relatorio_json


def main():
    parser = argparse.ArgumentParser(description="Motor de Cálculo de Reembolso de Despesas - CLI")
    subparsers = parser.add_subparsers(dest="comando", help="Comando a ser executado")

    calc_parser = subparsers.add_parser("calcular", help="Calcula reembolsos a partir de um JSON de entrada")
    calc_parser.add_argument("--input", required=True, help="Caminho do arquivo JSON de entrada")
    calc_parser.add_argument("--output", required=True, help="Caminho do arquivo JSON de saída")

    args = parser.parse_args()

    if args.comando == "calcular":
        try:
            colaborador, periodo, despesas = parse_input_file(args.input)
            resultados = processar_relatorio_despesas(colaborador, periodo, despesas)
            relatorio = construir_relatorio_saida(colaborador, periodo, resultados)
            salvar_relatorio_json(relatorio, args.output)
            print(f"Sucesso: Reembolsos calculados e salvos em '{args.output}'.")
            sys.exit(0)
        except Exception as e:
            print(f"Erro ao processar reembolso: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
