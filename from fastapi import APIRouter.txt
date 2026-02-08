from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/v1", tags=["Calculadora Deságio"])

class CalculoRequest(BaseModel):
    valor_precatorio: float
    prazo_estimado: int  # meses
    taxa_desagio: float  # % (ex: 20 = 20%)
    tribunal: str
    natureza: str  # "comum" ou "alimentar"

class CalculoResponse(BaseModel):
    valor_aquisicao: float
    lucro_bruto: float
    rentabilidade: float  # %
    tir_anual: float  # %
    score_risco: int  # 0-100
    score_oportunidade: int  # 0-100
    recomendacao: str

# Base de dados de histórico de tribunais (mock)
HISTORICO_TRIBUNAIS = {
    "TJ-BA": {"confiabilidade": 85, "tempo_medio_pagamento": 720},
    "TJ-SP": {"confiabilidade": 90, "tempo_medio_pagamento": 540},
    "TRF-3": {"confiabilidade": 95, "tempo_medio_pagamento": 480},
    "default": {"confiabilidade": 70, "tempo_medio_pagamento": 900}
}

def calcular_tir(valor_inicial: float, valor_final: float, prazo_meses: int) -> float:
    """Calcula TIR anualizada"""
    if prazo_meses == 0:
        return 0.0
    tir = ((valor_final / valor_inicial) ** (12 / prazo_meses) - 1) * 100
    return round(tir, 2)

def calcular_score_risco(tribunal: str, prazo: int) -> int:
    """Calcula score de risco (0-100, quanto maior, menor o risco)"""
    dados = HISTORICO_TRIBUNAIS.get(tribunal, HISTORICO_TRIBUNAIS["default"])
    
    score = dados["confiabilidade"]
    
    # Penaliza prazos muito longos
    if prazo > 24:
        score -= 10
    if prazo > 36:
        score -= 10
    
    return max(0, min(100, score))

def calcular_score_oportunidade(tir: float, score_risco: int) -> int:
    """Calcula score de oportunidade (0-100)"""
    # TIR acima de 18% a.a. é excelente
    score_tir = min(100, (tir / 18) * 80)
    
    # Combina TIR com risco
    score = (score_tir * 0.7) + (score_risco * 0.3)
    
    return int(score)

@router.post("/calculadora/desagio", response_model=CalculoResponse)
async def calcular_desagio(calc: CalculoRequest):
    """
    Calcula análise completa de viabilidade de aquisição
    """
    # Cálculos básicos
    valor_aquisicao = calc.valor_precatorio * (1 - calc.taxa_desagio / 100)
    lucro_bruto = calc.valor_precatorio - valor_aquisicao
    rentabilidade = (lucro_bruto / valor_aquisicao) * 100
    
    # TIR anualizada
    tir = calcular_tir(valor_aquisicao, calc.valor_precatorio, calc.prazo_estimado)
    
    # Scores
    score_risco = calcular_score_risco(calc.tribunal, calc.prazo_estimado)
    score_oportunidade = calcular_score_oportunidade(tir, score_risco)
    
    # Recomendação
    if tir >= 18 and score_risco >= 70:
        recomendacao = "🟢 EXCELENTE OPORTUNIDADE - Comprar"
    elif tir >= 12 and score_risco >= 60:
        recomendacao = "🟡 OPORTUNIDADE MODERADA - Avaliar"
    else:
        recomendacao = "🔴 RISCO ELEVADO - Rejeitar"
    
    return CalculoResponse(
        valor_aquisicao=round(valor_aquisicao, 2),
        lucro_bruto=round(lucro_bruto, 2),
        rentabilidade=round(rentabilidade, 2),
        tir_anual=tir,
        score_risco=score_risco,
        score_oportunidade=score_oportunidade,
        recomendacao=recomendacao
    )

@router.get("/calculadora/tribunais")
async def listar_tribunais():
    """Lista histórico de tribunais"""
    return HISTORICO_TRIBUNAIS