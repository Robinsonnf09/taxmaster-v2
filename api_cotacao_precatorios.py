from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import aiohttp
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/v1", tags=["Cotação Precatórios"])

class PrecatorioRequest(BaseModel):
    numero_oficio: str
    tribunal: str
    valor_face: float
    natureza: str  # "comum" ou "alimentar"
    prazo_estimado: int  # dias

class PropostaFundo(BaseModel):
    fundo_id: str
    nome_fundo: str
    valor_oferta: float
    desagio: float
    prazo_pagamento: int
    condicoes: str

class CotacaoResponse(BaseModel):
    cotacao_id: str
    fundos_interessados: int
    melhor_oferta: Optional[PropostaFundo]
    propostas: List[PropostaFundo]
    timestamp: str

# Simulação de fundos parceiros (em produção, seria chamada real)
FUNDOS_MOCK = [
    {"id": "fundo_alpha", "nome": "Alpha Precatórios", "desagio_base": 0.15},
    {"id": "fundo_beta", "nome": "Beta Investimentos", "desagio_base": 0.18},
    {"id": "fundo_gamma", "nome": "Gamma Capital", "desagio_base": 0.16},
]

async def consultar_fundo(fundo: dict, precatorio: PrecatorioRequest):
    """Simula consulta assíncrona a um fundo parceiro"""
    await asyncio.sleep(0.5)  # Simula latência de rede
    
    # Cálculo de deságio baseado em natureza e prazo
    desagio = fundo["desagio_base"]
    if precatorio.natureza == "alimentar":
        desagio -= 0.02  # Preferência alimentar = menor deságio
    
    if precatorio.prazo_estimado > 365:
        desagio += 0.05  # Prazo longo = maior deságio
    
    valor_oferta = precatorio.valor_face * (1 - desagio)
    
    return PropostaFundo(
        fundo_id=fundo["id"],
        nome_fundo=fundo["nome"],
        valor_oferta=round(valor_oferta, 2),
        desagio=round(desagio * 100, 2),
        prazo_pagamento=5,
        condicoes="Pagamento à vista após cessão"
    )

@router.post("/precatorio/cotacao", response_model=CotacaoResponse)
async def criar_cotacao(precatorio: PrecatorioRequest):
    """
    Solicita cotação em múltiplos fundos parceiros simultaneamente
    """
    cotacao_id = str(uuid.uuid4())
    
    # Consulta todos os fundos em paralelo
    tasks = [consultar_fundo(fundo, precatorio) for fundo in FUNDOS_MOCK]
    propostas = await asyncio.gather(*tasks)
    
    # Ordena por melhor oferta
    propostas_ordenadas = sorted(propostas, key=lambda x: x.valor_oferta, reverse=True)
    
    return CotacaoResponse(
        cotacao_id=cotacao_id,
        fundos_interessados=len(propostas_ordenadas),
        melhor_oferta=propostas_ordenadas[0] if propostas_ordenadas else None,
        propostas=propostas_ordenadas,
        timestamp=datetime.now().isoformat()
    )

@router.get("/fundos/ativos")
async def listar_fundos():
    """Lista fundos parceiros conectados"""
    return {
        "total": len(FUNDOS_MOCK),
        "fundos": FUNDOS_MOCK
    }

@router.get("/cotacao/{cotacao_id}")
async def consultar_cotacao(cotacao_id: str):
    """Consulta status de uma cotação"""
    return {
        "cotacao_id": cotacao_id,
        "status": "concluida",
        "message": "Cotação processada com sucesso"
    }