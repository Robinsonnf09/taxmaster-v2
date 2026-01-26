"""
Modelo para buscas de ofícios requisitórios
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BuscaOficio(Base):
    """Registro de busca de ofício"""
    __tablename__ = 'buscas_oficios'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Dados do precatório
    numero_processo = Column(String(50), nullable=False, index=True)
    numero_precatorio = Column(String(50), index=True)
    tribunal = Column(String(20), nullable=False)  # TJ-BA, TRF1, etc
    valor = Column(Float)
    natureza = Column(String(50))
    
    # Status da busca
    status = Column(String(20), default='pendente')  # pendente, processando, sucesso, erro
    progresso = Column(Integer, default=0)  # 0-100
    
    # Resultado
    oficio_encontrado = Column(Boolean, default=False)
    oficio_url = Column(String(500))
    oficio_path = Column(String(500))  # Caminho local do arquivo baixado
    
    # Metadados
    erro_mensagem = Column(Text)
    tentativas = Column(Integer, default=0)
    data_busca = Column(DateTime, default=datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Usuario
    usuario = Column(String(100))
    lote_id = Column(String(50), index=True)  # ID do lote de buscas
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero_processo': self.numero_processo,
            'numero_precatorio': self.numero_precatorio,
            'tribunal': self.tribunal,
            'valor': self.valor,
            'status': self.status,
            'progresso': self.progresso,
            'oficio_encontrado': self.oficio_encontrado,
            'oficio_url': self.oficio_url,
            'oficio_path': self.oficio_path,
            'erro_mensagem': self.erro_mensagem,
            'data_busca': self.data_busca.isoformat() if self.data_busca else None,
            'lote_id': self.lote_id
        }

class ConfiguracaoCertificado(Base):
    """Configuração do certificado digital"""
    __tablename__ = 'configuracoes_certificado'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Certificado
    certificado_path = Column(String(500), nullable=False)
    senha_hash = Column(String(500))  # Senha criptografada
    tipo = Column(String(10), default='A1')  # A1, A3
    validade = Column(DateTime)
    
    # Metadados
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
