from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import sys
sys.path.append("src")
from database import SessionLocal, Processo

app = FastAPI(title="TaxMaster CRM API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Schemas
class ProcessoResponse(BaseModel):
    id: int
    numero_processo: str
    tribunal: str
    valor_atualizado: Optional[float]
    score_oportunidade: Optional[float]
    fase: Optional[str]
    
    class Config:
        from_attributes = True

@app.get("/")
def read_root():
    return {"message": "TaxMaster CRM API v1.0", "status": "online"}

@app.get("/processos", response_model=List[ProcessoResponse])
def listar_processos(
    skip: int = 0,
    limit: int = 100,
    tribunal: Optional[str] = None,
    score_minimo: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """Lista todos os processos com filtros opcionais"""
    query = db.query(Processo)
    
    if tribunal:
        query = query.filter(Processo.tribunal == tribunal)
    
    if score_minimo:
        query = query.filter(Processo.score_oportunidade >= score_minimo)
    
    processos = query.offset(skip).limit(limit).all()
    return processos

@app.get("/processos/{numero_processo}")
def buscar_processo(numero_processo: str, db: Session = Depends(get_db)):
    """Busca processo especifico por numero"""
    processo = db.query(Processo).filter(
        Processo.numero_processo == numero_processo
    ).first()
    
    if not processo:
        raise HTTPException(status_code=404, detail="Processo nao encontrado")
    
    return processo

@app.get("/oportunidades")
def listar_oportunidades(
    score_minimo: float = 8.0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Lista as melhores oportunidades (score alto)"""
    processos = db.query(Processo).filter(
        Processo.score_oportunidade >= score_minimo
    ).order_by(Processo.score_oportunidade.desc()).limit(limit).all()
    
    return processos

@app.get("/estatisticas")
def obter_estatisticas(db: Session = Depends(get_db)):
    """Retorna estatisticas gerais"""
    total = db.query(Processo).count()
    valor_total = db.query(func.sum(Processo.valor_atualizado)).scalar() or 0
    
    por_tribunal = db.query(
        Processo.tribunal,
        func.count(Processo.id).label("total")
    ).group_by(Processo.tribunal).all()
    
    return {
        "total_processos": total,
        "valor_total_estoque": valor_total,
        "distribuicao_tribunais": {t: c for t, c in por_tribunal}
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
