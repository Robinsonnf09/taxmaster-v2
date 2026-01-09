from models_calculadora import Base, CalculoPrecatorio
from sqlalchemy import create_engine

engine = create_engine('sqlite:///calculos_precatorios.db')
Base.metadata.create_all(engine)
print("Tabelas criadas com sucesso!")
