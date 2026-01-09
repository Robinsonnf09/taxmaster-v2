from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class CalculoPrecatorio(Base):
    """Modelo para armazenar cálculos de precatórios"""
    __tablename__ = 'calculos_precatorios'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Dados do cálculo
    valor_original = Column(Float, nullable=False)
    indice_correcao = Column(String(50), nullable=False)
    data_inicial = Column(DateTime, nullable=False)
    data_final = Column(DateTime, nullable=False)
    
    # Juros e taxas
    incluir_juros = Column(Boolean, default=False)
    taxa_juros = Column(Float, default=0.0)
    percentual_honorarios = Column(Float, default=0.0)
    
    # Resultados
    valor_corrigido = Column(Float)
    valor_juros = Column(Float)
    valor_honorarios = Column(Float)
    valor_liquido = Column(Float)
    
    # Detalhamento
    detalhamento_json = Column(Text)  # JSON com detalhes mensais
    
    # Metadados
    usuario = Column(String(100))
    processo = Column(String(100))
    observacoes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'valor_original': self.valor_original,
            'indice_correcao': self.indice_correcao,
            'data_inicial': self.data_inicial.isoformat() if self.data_inicial else None,
            'data_final': self.data_final.isoformat() if self.data_final else None,
            'incluir_juros': self.incluir_juros,
            'taxa_juros': self.taxa_juros,
            'percentual_honorarios': self.percentual_honorarios,
            'valor_corrigido': self.valor_corrigido,
            'valor_juros': self.valor_juros,
            'valor_honorarios': self.valor_honorarios,
            'valor_liquido': self.valor_liquido,
            'processo': self.processo,
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
