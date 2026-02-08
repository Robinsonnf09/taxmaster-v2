from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import hashlib
from datetime import datetime

router = APIRouter(prefix="/api/v1", tags=["Blockchain"])

class RegistroBlockchainRequest(BaseModel):
    numero_precatorio: str
    cedente_wallet: str
    cessionario_wallet: str
    valor_cessao: float
    documento_base64: Optional[str] = None

class RegistroBlockchainResponse(BaseModel):
    transaction_hash: str
    contract_address: str
    cessao_id: int
    hash_documento: str
    timestamp: str
    gas_usado: int
    custo_eth: float

def gerar_hash_documento(conteudo: str) -> str:
    """Gera SHA-256 do documento"""
    return hashlib.sha256(conteudo.encode()).hexdigest()

@router.post("/blockchain/registrar", response_model=RegistroBlockchainResponse)
async def registrar_blockchain(registro: RegistroBlockchainRequest):
    """
    Registra cessão de precatório na blockchain
    (Mock - em produção: Web3.py + contrato real)
    """
    # Hash do documento
    hash_doc = gerar_hash_documento(
        f"{registro.numero_precatorio}{registro.cedente_wallet}{registro.cessionario_wallet}"
    )
    
    # Simula transação blockchain
    tx_hash = f"0x{hashlib.sha256(f'{datetime.now().isoformat()}'.encode()).hexdigest()}"
    
    return RegistroBlockchainResponse(
        transaction_hash=tx_hash,
        contract_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        cessao_id=1001,
        hash_documento=hash_doc,
        timestamp=datetime.now().isoformat(),
        gas_usado=85420,
        custo_eth=0.0012
    )

@router.get("/blockchain/verificar/{hash_documento}")
async def verificar_documento(hash_documento: str):
    """Verifica autenticidade de documento na blockchain"""
    return {
        "existe": True,
        "cessao_id": 1001,
        "timestamp_registro": "2026-02-06T10:30:00",
        "bloco": 18562341,
        "confirmacoes": 256
    }

@router.get("/blockchain/cessao/{cessao_id}")
async def consultar_cessao_blockchain(cessao_id: int):
    """Consulta cessão registrada"""
    return {
        "cessao_id": cessao_id,
        "numero_precatorio": "PRE-2024-12345",
        "cedente": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "cessionario": "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063",
        "valor_cessao": 500000.00,
        "timestamp": "2026-02-06T10:30:00",
        "ativa": True
    }