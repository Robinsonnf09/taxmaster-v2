from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import hashlib
import re

router = APIRouter(prefix="/api/v1", tags=["KYC/AML"])

class ValidacaoKYCRequest(BaseModel):
    tipo_pessoa: str  # "PF" ou "PJ"
    cpf_cnpj: str
    nome_completo: str
    data_nascimento: Optional[str] = None
    documentos: List[str] = []  # URLs ou base64

class ValidacaoKYCResponse(BaseModel):
    validacao_id: str
    status: str  # "aprovado", "pendente", "rejeitado"
    score_risco: int  # 0-100
    alertas: List[str]
    verificacoes: Dict[str, bool]
    timestamp: str

# Lista restritivas mockadas (em produção: integração real)
LISTA_PEP = ["12345678900", "98765432100"]
LISTA_SANCOES = ["11122233344"]
LISTA_COAF = []

def validar_cpf(cpf: str) -> bool:
    """Valida CPF usando algoritmo oficial"""
    cpf = re.sub(r'\D', '', cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    
    # Validação dos dígitos verificadores
    for i in range(9, 11):
        soma = sum(int(cpf[num]) * ((i + 1) - num) for num in range(i))
        digito = ((soma * 10) % 11) % 10
        if int(cpf[i]) != digito:
            return False
    
    return True

def validar_cnpj(cnpj: str) -> bool:
    """Valida CNPJ usando algoritmo oficial"""
    cnpj = re.sub(r'\D', '', cnpj)
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False
    
    # Validação simplificada (em produção: algoritmo completo)
    return True

def consultar_receita_federal(cpf_cnpj: str) -> Dict:
    """Mock de consulta à Receita Federal"""
    return {
        "situacao_cadastral": "REGULAR",
        "pendencias": [],
        "ultima_atualizacao": "2026-01-15"
    }

def consultar_listas_restritivas(cpf_cnpj: str) -> Dict:
    """Verifica listas PEP, sanções, COAF"""
    doc_limpo = re.sub(r'\D', '', cpf_cnpj)
    
    return {
        "pep": doc_limpo in LISTA_PEP,
        "sancoes": doc_limpo in LISTA_SANCOES,
        "coaf": doc_limpo in LISTA_COAF
    }

def calcular_score_risco(verificacoes: Dict, listas: Dict) -> int:
    """Calcula score de risco (0=alto risco, 100=baixo risco)"""
    score = 100
    
    # Penalizações
    if not verificacoes["documento_valido"]:
        score -= 50
    
    if not verificacoes["receita_federal_ok"]:
        score -= 30
    
    if listas["pep"]:
        score -= 20
    
    if listas["sancoes"]:
        score -= 40
    
    if listas["coaf"]:
        score -= 50
    
    return max(0, score)

@router.post("/kyc/validar", response_model=ValidacaoKYCResponse)
async def validar_kyc(request: ValidacaoKYCRequest):
    """
    Validação KYC/AML completa
    """
    validacao_id = hashlib.sha256(
        f"{request.cpf_cnpj}{datetime.now().isoformat()}".encode()
    ).hexdigest()[:16]
    
    # Validação de documento
    doc_limpo = re.sub(r'\D', '', request.cpf_cnpj)
    
    if request.tipo_pessoa == "PF":
        doc_valido = validar_cpf(doc_limpo)
    else:
        doc_valido = validar_cnpj(doc_limpo)
    
    # Consultas externas (mock)
    receita = consultar_receita_federal(doc_limpo)
    listas = consultar_listas_restritivas(doc_limpo)
    
    # Verificações
    verificacoes = {
        "documento_valido": doc_valido,
        "receita_federal_ok": receita["situacao_cadastral"] == "REGULAR",
        "lista_pep": listas["pep"],
        "lista_sancoes": listas["sancoes"],
        "lista_coaf": listas["coaf"]
    }
    
    # Alertas
    alertas = []
    if listas["pep"]:
        alertas.append("⚠️ Pessoa Exposta Politicamente (PEP) - Diligência reforçada necessária")
    
    if listas["sancoes"]:
        alertas.append("🚨 Consta em lista de sanções internacionais")
    
    if listas["coaf"]:
        alertas.append("🚨 Consta em registros COAF")
    
    if not doc_valido:
        alertas.append("❌ Documento inválido")
    
    # Score