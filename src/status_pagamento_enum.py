"""
Atualização do modelo para incluir status de pagamento detalhado
"""

import enum
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class StatusPagamentoEnum(enum.Enum):
    """Status detalhado de pagamento"""
    COM_PENDENCIA = "Com Pendência"
    PRONTO_PARA_PAGAMENTO = "Pronto para Pagamento (Sem Pendência)"
    EM_PROCESSAMENTO = "Em Processamento de Pagamento"
    PAGO = "Pago"
    CANCELADO = "Cancelado"

# Adicionar ao modelo Processo existente:
# status_pagamento = Column(SQLEnum(StatusPagamentoEnum), default=StatusPagamentoEnum.COM_PENDENCIA, index=True)
# data_pagamento = Column(Date)
# valor_pago = Column(Float)
