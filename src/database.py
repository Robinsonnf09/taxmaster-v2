"""
Configuração do banco de dados SQLite
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Configuração do banco de dados SQLite
DATABASE_URL = "sqlite:///taxmaster.db"

# Criar engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

# Criar sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()

def init_db():
    """Inicializa o banco de dados"""
    from models_atualizado import Base as ModelsBase
    ModelsBase.metadata.create_all(bind=engine)
    print("[OK] Banco SQLite criado com sucesso: taxmaster.db")

# Criar banco automaticamente ao importar
init_db()
