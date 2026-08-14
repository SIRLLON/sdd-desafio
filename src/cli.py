"""
Interface de Linha de Comando (CLI) para a execução do motor de reembolso v2.0.
Uso: python -m src.cli calcular --input despesas.json --output resultado.json [--politica politica.json] [--cambio cambio.json]
"""
import sys
import argparse
from src.parser import parse_input_file, GerenciadorCambio
from src.engine import processar_relatorio_despesas, GerenciadorPolitica
from src.formatter import construir_relatorio_saida, salvar_relatorio_json


def main():
    parser = argparse.ArgumentParser(description="Motor de Cálculo de Reembolso de Despesas - CLI v2.0")
    subparsers = parser.add_subparsers(dest="comando", help="Comando a ser executado")

    calc_parser = subparsers.add_parser("calcular", help="Calcula reembolsos a partir de um JSON de entrada")
    calc_parser.add_argument("--input", required=True, help="Caminho do arquivo JSON de entrada")
    calc_parser.add_argument("--output", required=True, help="Caminho do arquivo JSON de saída")
    calc_parser.add_argument("--politica", required=False, default=None, help="Caminho opcional do arquivo de política JSON (ex: politica-v4.json)")
    calc_parser.add_argument("--cambio", required=False, default=None, help="Caminho opcional do arquivo de taxas de câmbio JSON (ex: cambio.json)")

    args = parser.parse_args()

    if args.comando == "calcular":
        try:
            gerenciador_cambio = GerenciadorCambio.carregar(args.cambio) if args.cambio else None
            gerenciador_politica = GerenciadorPolitica.carregar(args.politica) if args.politica else None

            colaborador, periodo, despesas = parse_input_file(args.input, gerenciador_cambio)
            resultados = processar_relatorio_despesas(colaborador, periodo, despesas, gerenciador_politica)
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
