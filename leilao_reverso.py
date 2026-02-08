from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime, timedelta
import asyncio
import json

router = APIRouter(prefix="/api/v1", tags=["Leilão Reverso"])

class LeilaoCreate(BaseModel):
    precatorio_id: str
    valor_inicial: float
    duracao_minutos: int
    lance_minimo: float

class LanceCreate(BaseModel):
    leilao_id: str
    fundo_id: str
    valor_lance: float

# Armazenamento em memória (em produção, usar Redis/DB)
leiloes_ativos: Dict = {}
conexoes_websocket: List[WebSocket] = []

@router.post("/leilao/criar")
async def criar_leilao(leilao: LeilaoCreate):
    """Cria novo leilão reverso"""
    leilao_id = f"leilao_{datetime.now().timestamp()}"
    
    leiloes_ativos[leilao_id] = {
        "id": leilao_id,
        "precatorio_id": leilao.precatorio_id,
        "valor_atual": leilao.valor_inicial,
        "lances": [],
        "inicio": datetime.now().isoformat(),
        "fim": (datetime.now() + timedelta(minutes=leilao.duracao_minutos)).isoformat(),
        "status": "ativo"
    }
    
    return {
        "leilao_id": leilao_id,
        "message": "Leilão criado com sucesso",
        "dados": leiloes_ativos[leilao_id]
    }

@router.post("/leilao/lance")
async def registrar_lance(lance: LanceCreate):
    """Registra novo lance em leilão"""
    if lance.leilao_id not in leiloes_ativos:
        return {"error": "Leilão não encontrado"}
    
    leilao = leiloes_ativos[lance.leilao_id]
    
    if leilao["status"] != "ativo":
        return {"error": "Leilão encerrado"}
    
    # Valida se é lance válido (maior que atual)
    if lance.valor_lance <= leilao["valor_atual"]:
        return {"error": "Lance deve ser maior que o valor atual"}
    
    # Registra lance
    novo_lance = {
        "fundo_id": lance.fundo_id,
        "valor": lance.valor_lance,
        "timestamp": datetime.now().isoformat()
    }
    
    leilao["lances"].append(novo_lance)
    leilao["valor_atual"] = lance.valor_lance
    
    # Notifica via WebSocket
    await notificar_novo_lance(lance.leilao_id, novo_lance)
    
    return {
        "success": True,
        "lance": novo_lance,
        "total_lances": len(leilao["lances"])
    }

@router.get("/leilao/{leilao_id}")
async def consultar_leilao(leilao_id: str):
    """Consulta status do leilão"""
    if leilao_id not in leiloes_ativos:
        return {"error": "Leilão não encontrado"}
    
    return leiloes_ativos[leilao_id]

@router.get("/leilao/ativos/listar")
async def listar_leiloes():
    """Lista todos os leilões ativos"""
    return {
        "total": len(leiloes_ativos),
        "leiloes": list(leiloes_ativos.values())
    }

async def notificar_novo_lance(leilao_id: str, lance: dict):
    """Notifica clientes WebSocket sobre novo lance"""
    mensagem = json.dumps({
        "evento": "novo_lance",
        "leilao_id": leilao_id,
        "lance": lance
    })
    
    for ws in conexoes_websocket:
        try:
            await ws.send_text(mensagem)
        except:
            pass

@router.websocket("/ws/leilao/{leilao_id}")
async def websocket_leilao(websocket: WebSocket, leilao_id: str):
    """WebSocket para notificações em tempo real"""
    await websocket.accept()
    conexoes_websocket.append(websocket)
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        conexoes_websocket.remove(websocket)