"""
Atualização do modelo para incluir rastreamento de ofício requisitório
"""

import enum
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class StatusOficioEnum(enum.Enum):
    """Status detalhado do ofício requisitório"""
    NAO_EXPEDIDO = "Não Expedido"
    EM_ELABORACAO = "Em Elaboração"
    AGUARDANDO_ASSINATURA = "Aguardando Assinatura"
    ASSINADO = "Assinado"
    EXPEDIDO = "Expedido"
    ENVIADO_TRIBUNAL = "Enviado ao Tribunal"
    RECEBIDO_TRIBUNAL = "Recebido pelo Tribunal"
    EM_CONFERENCIA = "Em Conferência"
    RETIFICADO = "Retificado"
    REGISTRADO = "Registrado como Precatório"
    INSCRITO_ORCAMENTO = "Inscrito no Orçamento"
    EM_LISTA_PAGAMENTO = "Em Lista de Pagamento"
    PAGO = "Pago"

class AtualizacaoOficio(Base):
    """Histórico de atualizações do ofício requisitório"""
    __tablename__ = "atualizacoes_oficio"
    
    id = Column(Integer, primary_key=True, index=True)
    processo_id = Column(Integer, ForeignKey("processos.id"), nullable=False)
    
    # Dados da atualização
    data_atualizacao = Column(DateTime, default=datetime.now, nullable=False, index=True)
    status_anterior = Column(SQLEnum(StatusOficioEnum))
    status_novo = Column(SQLEnum(StatusOficioEnum), nullable=False)
    
    # Detalhes
    descricao = Column(Text)
    observacoes = Column(Text)
    valor_atualizado = Column(Float)
    
    # Documentos
    numero_oficio = Column(String(50))
    numero_precatorio = Column(String(50))
    
    # Origem da atualização
    origem = Column(String(50))  # MANUAL, AUTOMATICA, IMPORTACAO, SCRAPING
    usuario = Column(String(100))
    
    # Validação
    validado = Column(Boolean, default=False)
    data_validacao = Column(DateTime)
    
    # Relacionamento
    processo = relationship("Processo", back_populates="atualizacoes_oficio")

# Adicionar ao modelo Processo existente:
# status_oficio = Column(SQLEnum(StatusOficioEnum), default=StatusOficioEnum.NAO_EXPEDIDO, index=True)
# data_ultima_atualizacao_oficio = Column(DateTime)
# atualizacoes_oficio = relationship("AtualizacaoOficio", back_populates="processo", cascade="all, delete-orphan")
