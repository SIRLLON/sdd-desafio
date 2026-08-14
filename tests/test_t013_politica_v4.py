"""
Testes para T-013 — Leitor de Políticas por Centro de Custo (politica-v4.json) e Fallbacks.
Atende: RN-015, RN-016, RN-017, AMB-014, AMB-015
"""
import os
from src.parser import float_to_cents
from src.engine import GerenciadorPolitica


def test_politica_centro_custo_e_fallback():
    """Valida leitura de politica-v4.json, limites por CC, fallback padrao e teto 0.00."""
    filepath = os.path.join("exemplos", "envelope", "politica-v4.json")
    gerenciador = GerenciadorPolitica.carregar(filepath)

    # CC-COMERCIAL: alimentacao R$ 90.00 (9000 centavos), representacao R$ 300.00 (30000 centavos)
    lim_alim_comercial = gerenciador.obter_limite_centavos("CC-COMERCIAL", "alimentacao")
    assert lim_alim_comercial == 9000

    lim_rep_comercial = gerenciador.obter_limite_centavos("CC-COMERCIAL", "representacao")
    assert lim_rep_comercial == 30000

    # CC-ENG-PLATAFORMA: hospedagem R$ 0.00 (0 centavos -> proibido)
    lim_hosp_eng = gerenciador.obter_limite_centavos("CC-ENG-PLATAFORMA", "hospedagem")
    assert lim_hosp_eng == 0

    # CC-SUPORTE-N2 (não cadastrado): fallback padrao (alimentacao R$ 60.00 = 6000 centavos)
    lim_alim_sup = gerenciador.obter_limite_centavos("CC-SUPORTE-N2", "alimentacao")
    assert lim_alim_sup == 6000

    # Categoria representacao no CC-SUPORTE-N2 (não existe em CC-SUPORTE-N2 nem no padrao) -> None (inválido)
    lim_rep_sup = gerenciador.obter_limite_centavos("CC-SUPORTE-N2", "representacao")
    assert lim_rep_sup is None
