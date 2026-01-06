"""
Módulo de Cobertura Nacional - Tribunais Brasileiros
Acesso a dados de tribunais estaduais, federais e trabalhistas
"""

TRIBUNAIS_DISPONIVEIS = {
    "ESTADUAIS": {
        "TJSP": {"nome": "Tribunal de Justiça de São Paulo", "uf": "SP", "url": "https://esaj.tjsp.jus.br"},
        "TJRJ": {"nome": "Tribunal de Justiça do Rio de Janeiro", "uf": "RJ", "url": "https://www4.tjrj.jus.br"},
        "TJMG": {"nome": "Tribunal de Justiça de Minas Gerais", "uf": "MG", "url": "https://www4.tjmg.jus.br"},
        "TJRS": {"nome": "Tribunal de Justiça do Rio Grande do Sul", "uf": "RS", "url": "https://www.tjrs.jus.br"},
        "TJPR": {"nome": "Tribunal de Justiça do Paraná", "uf": "PR", "url": "https://www.tjpr.jus.br"},
        "TJSC": {"nome": "Tribunal de Justiça de Santa Catarina", "uf": "SC", "url": "https://esaj.tjsc.jus.br"},
        "TJBA": {"nome": "Tribunal de Justiça da Bahia", "uf": "BA", "url": "https://esaj.tjba.jus.br"},
        "TJPE": {"nome": "Tribunal de Justiça de Pernambuco", "uf": "PE", "url": "https://www.tjpe.jus.br"},
        "TJCE": {"nome": "Tribunal de Justiça do Ceará", "uf": "CE", "url": "https://esaj.tjce.jus.br"},
        "TJGO": {"nome": "Tribunal de Justiça de Goiás", "uf": "GO", "url": "https://projudi.tjgo.jus.br"},
    },
    "FEDERAIS": {
        "TRF1": {"nome": "Tribunal Regional Federal da 1ª Região", "estados": ["DF", "GO", "TO", "MT", "BA", "PI", "MA", "PA", "AP", "RR", "RO", "AC", "AM"], "url": "https://www.trf1.jus.br"},
        "TRF2": {"nome": "Tribunal Regional Federal da 2ª Região", "estados": ["RJ", "ES"], "url": "https://www.trf2.jus.br"},
        "TRF3": {"nome": "Tribunal Regional Federal da 3ª Região", "estados": ["SP", "MS"], "url": "https://www.trf3.jus.br"},
        "TRF4": {"nome": "Tribunal Regional Federal da 4ª Região", "estados": ["RS", "SC", "PR"], "url": "https://www.trf4.jus.br"},
        "TRF5": {"nome": "Tribunal Regional Federal da 5ª Região", "estados": ["CE", "AL", "SE", "PB", "RN", "PE"], "url": "https://www.trf5.jus.br"},
        "TRF6": {"nome": "Tribunal Regional Federal da 6ª Região", "estados": ["MG"], "url": "https://www.trf6.jus.br"},
    },
    "TRABALHISTAS": {
        "TST": {"nome": "Tribunal Superior do Trabalho", "url": "https://www.tst.jus.br"},
        "TRT2": {"nome": "TRT da 2ª Região (SP)", "uf": "SP", "url": "https://www.trt2.jus.br"},
        "TRT15": {"nome": "TRT da 15ª Região (Campinas)", "uf": "SP", "url": "https://www.trt15.jus.br"},
    }
}

def obter_estatisticas_cobertura():
    """Retorna estatísticas de cobertura nacional"""
    return {
        "total_tribunais": sum(len(t) for t in TRIBUNAIS_DISPONIVEIS.values()),
        "estaduais": len(TRIBUNAIS_DISPONIVEIS["ESTADUAIS"]),
        "federais": len(TRIBUNAIS_DISPONIVEIS["FEDERAIS"]),
        "trabalhistas": len(TRIBUNAIS_DISPONIVEIS["TRABALHISTAS"]),
        "estados_cobertos": 27,
        "cobertura_percentual": 100
    }
