"""
Script para popular o banco de dados com dados de exemplo
"""

import sys
sys.path.append("src")

from database import SessionLocal
from models_atualizado import Processo, TribunalEnum, NaturezaEnum, StatusProcessoEnum
from datetime import datetime, date

def criar_processos_exemplo():
    """Cria processos de exemplo no banco"""
    db = SessionLocal()
    
    try:
        # Verificar se já existem processos
        count = db.query(Processo).count()
        
        if count > 0:
            print(f"[INFO] Banco já possui {count} processo(s)")
            return
        
        print("Criando processos de exemplo...")
        
        # Processo 1 - Com processo principal
        processo1 = Processo(
            numero_processo="0034565-98.2018.8.26.0053",
            processo_principal="0048680-71.2011.8.26.0053",
            tribunal=TribunalEnum.TJSP,
            natureza=NaturezaEnum.ALIMENTAR,
            status=StatusProcessoEnum.PENDENTE,
            
            credor_nome="João da Silva Santos",
            credor_cpf_cnpj="123.456.789-00",
            credor_email="joao.silva@email.com",
            credor_telefone="(11) 98765-4321",
            credor_idoso=True,
            
            advogado_nome="Dr. Carlos Oliveira",
            advogado_oab="123456/SP",
            advogado_email="carlos@adv.com.br",
            advogado_telefone="(11) 3333-4444",
            
            valor_principal=150000.00,
            valor_juros=25000.00,
            valor_atualizado=175000.00,
            
            classe="Execução de Título Judicial",
            assunto="Precatório Alimentar",
            area="Cível",
            
            observacoes="Processo prioritário - Credor idoso"
        )
        
        # Processo 2 - Sem processo principal
        processo2 = Processo(
            numero_processo="0012345-67.2020.8.26.0100",
            tribunal=TribunalEnum.TJSP,
            natureza=NaturezaEnum.COMUM,
            status=StatusProcessoEnum.EM_ANALISE,
            
            credor_nome="Maria Aparecida Costa",
            credor_cpf_cnpj="987.654.321-00",
            credor_email="maria.costa@email.com",
            credor_telefone="(11) 91234-5678",
            
            advogado_nome="Dra. Ana Paula Ferreira",
            advogado_oab="654321/SP",
            
            valor_principal=80000.00,
            valor_juros=15000.00,
            valor_atualizado=95000.00,
            
            classe="Execução de Título Extrajudicial",
            assunto="Precatório Comum"
        )
        
        # Processo 3 - Tributário
        processo3 = Processo(
            numero_processo="0098765-43.2019.8.26.0053",
            processo_principal="0011111-22.2015.8.26.0053",
            tribunal=TribunalEnum.TJSP,
            natureza=NaturezaEnum.TRIBUTARIO,
            status=StatusProcessoEnum.VALIDADO,
            
            credor_nome="Empresa XYZ Ltda",
            credor_cpf_cnpj="12.345.678/0001-90",
            credor_email="contato@empresaxyz.com.br",
            credor_telefone="(11) 4444-5555",
            
            advogado_nome="Dr. Roberto Almeida",
            advogado_oab="111222/SP",
            
            valor_principal=500000.00,
            valor_juros=120000.00,
            valor_atualizado=620000.00,
            
            classe="Ação de Repetição de Indébito",
            assunto="Precatório Tributário - ICMS",
            area="Tributário",
            
            tem_oficio=True
        )
        
        db.add_all([processo1, processo2, processo3])
        db.commit()
        
        print("[OK] 3 processos de exemplo criados com sucesso!")
        print("\nProcessos criados:")
        print("1. 0034565-98.2018.8.26.0053 (com processo principal)")
        print("2. 0012345-67.2020.8.26.0100 (sem processo principal)")
        print("3. 0098765-43.2019.8.26.0053 (tributário)")
        
    except Exception as e:
        db.rollback()
        print(f"[ERRO] {str(e)}")
        
    finally:
        db.close()

if __name__ == "__main__":
    criar_processos_exemplo()
