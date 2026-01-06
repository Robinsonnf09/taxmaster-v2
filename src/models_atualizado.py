"""
Atualização do modelo para incluir esfera do precatório
"""

import enum
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class EsferaEnum(enum.Enum):
    """Esfera do precatório"""
    ESTADUAL = "Estadual"
    MUNICIPAL = "Municipal"
    FEDERAL = "Federal"

class TribunalEnum(enum.Enum):
    """Tribunais suportados"""
    # Estaduais
    TJSP = "TJSP"
    TJRJ = "TJRJ"
    TJMG = "TJMG"
    TJRS = "TJRS"
    TJPR = "TJPR"
    TJSC = "TJSC"
    TJBA = "TJBA"
    TJPE = "TJPE"
    TJCE = "TJCE"
    TJGO = "TJGO"
    
    # Federais
    TRF1 = "TRF1"
    TRF2 = "TRF2"
    TRF3 = "TRF3"
    TRF4 = "TRF4"
    TRF5 = "TRF5"
    TRF6 = "TRF6"
    
    # Trabalhistas
    TST = "TST"
    TRT1 = "TRT1"
    TRT2 = "TRT2"
    TRT3 = "TRT3"
    TRT15 = "TRT15"

class NaturezaEnum(enum.Enum):
    """Natureza do precatório"""
    ALIMENTAR = "Alimentar"
    COMUM = "Comum"
    TRIBUTARIO = "Tributário"
    TRABALHISTA = "Trabalhista"

class StatusProcessoEnum(enum.Enum):
    """Status do processo"""
    PENDENTE = "Pendente"
    EM_ANALISE = "Em Análise"
    OFICIO_ENCONTRADO = "Ofício Encontrado"
    OFICIO_BAIXADO = "Ofício Baixado"
    VALIDADO = "Validado"
    NEGOCIACAO = "Em Negociação"
    CONCLUIDO = "Concluído"
    PAGO = "Pago"
    CANCELADO = "Cancelado"

class EntePagadorEnum(enum.Enum):
    """Ente devedor/pagador"""
    # Estaduais
    ESTADO_SP = "Estado de São Paulo"
    ESTADO_RJ = "Estado do Rio de Janeiro"
    ESTADO_MG = "Estado de Minas Gerais"
    ESTADO_RS = "Estado do Rio Grande do Sul"
    ESTADO_PR = "Estado do Paraná"
    
    # Municipais
    PREFEITURA_SP = "Prefeitura de São Paulo"
    PREFEITURA_RJ = "Prefeitura do Rio de Janeiro"
    PREFEITURA_BH = "Prefeitura de Belo Horizonte"
    PREFEITURA_POA = "Prefeitura de Porto Alegre"
    PREFEITURA_CURITIBA = "Prefeitura de Curitiba"
    
    # Federais
    UNIAO = "União Federal"
    INSS = "INSS"
    RECEITA_FEDERAL = "Receita Federal"
    FAZENDA_NACIONAL = "Fazenda Nacional"

class Processo(Base):
    """Modelo de Processo/Precatório"""
    __tablename__ = "processos"
    
    # Identificação
    id = Column(Integer, primary_key=True, index=True)
    numero_processo = Column(String(25), unique=True, index=True, nullable=False)
    processo_principal = Column(String(25), index=True)
    
    # Classificação
    tribunal = Column(SQLEnum(TribunalEnum), nullable=False, index=True)
    esfera = Column(SQLEnum(EsferaEnum), nullable=False, index=True)
    ente_pagador = Column(SQLEnum(EntePagadorEnum), index=True)
    natureza = Column(SQLEnum(NaturezaEnum), index=True)
    status = Column(SQLEnum(StatusProcessoEnum), default=StatusProcessoEnum.PENDENTE, index=True)
    
    # Credor
    credor_nome = Column(String(200), nullable=False, index=True)
    credor_cpf_cnpj = Column(String(18), index=True)
    credor_email = Column(String(100))
    credor_telefone = Column(String(20))
    credor_endereco = Column(Text)
    
    # Prioridades
    credor_idoso = Column(Boolean, default=False, index=True)
    credor_doenca_grave = Column(Boolean, default=False, index=True)
    credor_deficiente = Column(Boolean, default=False, index=True)
    
    # Devedor
    devedor_nome = Column(String(200))
    devedor_cpf_cnpj = Column(String(18))
    
    # Advogado
    advogado_nome = Column(String(200))
    advogado_oab = Column(String(20))
    advogado_email = Column(String(100))
    advogado_telefone = Column(String(20))
    
    # Valores
    valor_principal = Column(Float, nullable=False)
    valor_juros = Column(Float, default=0)
    valor_atualizado = Column(Float, nullable=False, index=True)
    data_base_calculo = Column(Date)
    
    # Informações processuais
    classe = Column(String(100))
    assunto = Column(String(200))
    area = Column(String(50))
    
    # Datas
    data_ajuizamento = Column(Date)
    data_transito_julgado = Column(Date)
    data_expedicao_oficio = Column(Date, index=True)
    data_inscricao_precatorio = Column(Date)
    ano_precatorio = Column(Integer, index=True)
    
    # Ofício Requisitório
    tem_oficio = Column(Boolean, default=False, index=True)
    numero_oficio = Column(String(50))
    caminho_oficio = Column(String(500))
    data_busca_oficio = Column(DateTime)
    hash_oficio = Column(String(64))
    
    # Pagamento
    possui_pendencia_pagamento = Column(Boolean, default=True, index=True)
    previsao_pagamento = Column(Date)
    ordem_cronologica = Column(Integer)
    
    # Metadata
    data_cadastro = Column(DateTime, default=datetime.now, index=True)
    data_atualizacao = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    usuario_cadastro = Column(String(100))
    
    # Observações
    observacoes = Column(Text)
    tags = Column(String(500))
    score_lead = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<Processo {self.numero_processo}>"

class LogBuscaOficio(Base):
    """Log de buscas de ofícios"""
    __tablename__ = "logs_busca_oficio"
    
    id = Column(Integer, primary_key=True)
    processo_id = Column(Integer, ForeignKey("processos.id"))
    data_busca = Column(DateTime, default=datetime.now)
    sucesso = Column(Boolean, default=False)
    mensagem = Column(Text)
    tempo_execucao = Column(Float)
    
    processo = relationship("Processo", backref="logs_busca")

class Contato(Base):
    """Contatos/Leads"""
    __tablename__ = "contatos"
    
    id = Column(Integer, primary_key=True)
    processo_id = Column(Integer, ForeignKey("processos.id"))
    
    nome = Column(String(200), nullable=False)
    tipo = Column(String(50))
    email_principal = Column(String(100))
    telefone_principal = Column(String(20))
    
    data_cadastro = Column(DateTime, default=datetime.now)
    
    processo = relationship("Processo", backref="contatos")
