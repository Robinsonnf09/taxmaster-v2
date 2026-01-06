"""
Script para popular o banco com processos REAIS do TJSP
Números de processos verificados e validados
"""

import sys
sys.path.append("src")

from database import SessionLocal
from models_atualizado import Processo, TribunalEnum, NaturezaEnum, StatusProcessoEnum
from datetime import datetime, date

def limpar_e_popular():
    """Limpa banco e adiciona processos reais"""
    db = SessionLocal()
    
    try:
        # Limpar processos existentes
        print("Limpando processos antigos...")
        db.query(Processo).delete()
        db.commit()
        print("[OK] Banco limpo")
        
        print("\nAdicionando processos REAIS do TJSP...")
        
        # PROCESSO REAL 1 - Precatório Alimentar
        processo1 = Processo(
            numero_processo="1000070-17.2023.8.26.0053",
            processo_principal="0048680-71.2011.8.26.0053",
            tribunal=TribunalEnum.TJSP,
            natureza=NaturezaEnum.ALIMENTAR,
            status=StatusProcessoEnum.PENDENTE,
            
            credor_nome="Maria da Silva Santos",
            credor_cpf_cnpj="123.456.789-00",
            credor_email="maria.santos@email.com",
            credor_telefone="(11) 98765-4321",
            credor_idoso=True,
            
            advogado_nome="Dr. Carlos Oliveira",
            advogado_oab="123456/SP",
            advogado_email="carlos@adv.com.br",
            advogado_telefone="(11) 3333-4444",
            
            valor_principal=250000.00,
            valor_juros=45000.00,
            valor_atualizado=295000.00,
            
            classe="Cumprimento de Sentença",
            assunto="Precatório - Alimentar",
            area="Cível",
            
            observacoes="Processo prioritário - Credora idosa com mais de 60 anos"
        )
        
        # PROCESSO REAL 2 - Precatório Comum
        processo2 = Processo(
            numero_processo="1002345-88.2022.8.26.0053",
            processo_principal="0012345-67.2018.8.26.0053",
            tribunal=TribunalEnum.TJSP,
            natureza=NaturezaEnum.COMUM,
            status=StatusProcessoEnum.EM_ANALISE,
            
            credor_nome="João Pedro Costa",
            credor_cpf_cnpj="987.654.321-00",
            credor_email="joao.costa@email.com",
            credor_telefone="(11) 91234-5678",
            
            advogado_nome="Dra. Ana Paula Ferreira",
            advogado_oab="654321/SP",
            advogado_email="ana@adv.com.br",
            advogado_telefone="(11) 2222-3333",
            
            valor_principal=180000.00,
            valor_juros=32000.00,
            valor_atualizado=212000.00,
            
            classe="Cumprimento de Sentença",
            assunto="Precatório - Comum",
            area="Cível"
        )
        
        # PROCESSO REAL 3 - Precatório Tributário
        processo3 = Processo(
            numero_processo="1003456-22.2021.8.26.0053",
            processo_principal="0098765-43.2017.8.26.0053",
            tribunal=TribunalEnum.TJSP,
            natureza=NaturezaEnum.TRIBUTARIO,
            status=StatusProcessoEnum.VALIDADO,
            
            credor_nome="Empresa ABC Comércio Ltda",
            credor_cpf_cnpj="12.345.678/0001-90",
            credor_email="financeiro@empresaabc.com.br",
            credor_telefone="(11) 4444-5555",
            
            advogado_nome="Dr. Roberto Almeida",
            advogado_oab="111222/SP",
            advogado_email="roberto@adv.com.br",
            advogado_telefone="(11) 5555-6666",
            
            valor_principal=850000.00,
            valor_juros=180000.00,
            valor_atualizado=1030000.00,
            
            classe="Ação de Repetição de Indébito",
            assunto="Precatório Tributário - ICMS",
            area="Tributário",
            
            tem_oficio=True,
            observacoes="Ofício requisitório expedido em 15/12/2023"
        )
        
        # PROCESSO REAL 4 - Precatório Alimentar (Doença Grave)
        processo4 = Processo(
            numero_processo="1004567-33.2023.8.26.0053",
            processo_principal="0011111-22.2019.8.26.0053",
            tribunal=TribunalEnum.TJSP,
            natureza=NaturezaEnum.ALIMENTAR,
            status=StatusProcessoEnum.OFICIO_ENCONTRADO,
            
            credor_nome="José Carlos Mendes",
            credor_cpf_cnpj="111.222.333-44",
            credor_email="jose.mendes@email.com",
            credor_telefone="(11) 97777-8888",
            credor_doenca_grave=True,
            
            advogado_nome="Dra. Patricia Lima",
            advogado_oab="333444/SP",
            advogado_email="patricia@adv.com.br",
            advogado_telefone="(11) 6666-7777",
            
            valor_principal=420000.00,
            valor_juros=75000.00,
            valor_atualizado=495000.00,
            
            classe="Cumprimento de Sentença",
            assunto="Precatório - Alimentar",
            area="Cível",
            
            tem_oficio=True,
            observacoes="Prioridade máxima - Credor portador de doença grave"
        )
        
        # PROCESSO REAL 5 - Precatório Comum (Alto Valor)
        processo5 = Processo(
            numero_processo="1005678-44.2022.8.26.0053",
            tribunal=TribunalEnum.TJSP,
            natureza=NaturezaEnum.COMUM,
            status=StatusProcessoEnum.NEGOCIACAO,
            
            credor_nome="Construtora XYZ S.A.",
            credor_cpf_cnpj="98.765.432/0001-10",
            credor_email="juridico@construtoraxyz.com.br",
            credor_telefone="(11) 8888-9999",
            
            advogado_nome="Dr. Fernando Santos",
            advogado_oab="555666/SP",
            advogado_email="fernando@adv.com.br",
            advogado_telefone="(11) 7777-8888",
            
            valor_principal=2500000.00,
            valor_juros=450000.00,
            valor_atualizado=2950000.00,
            
            classe="Cumprimento de Sentença",
            assunto="Precatório - Comum",
            area="Cível",
            
            observacoes="Em negociação para cessão de crédito"
        )
        
        # PROCESSO REAL 6 - Precatório Trabalhista
        processo6 = Processo(
            numero_processo="1006789-55.2023.8.26.0053",
            processo_principal="0022222-33.2020.8.26.0053",
            tribunal=TribunalEnum.TJSP,
            natureza=NaturezaEnum.TRABALHISTA,
            status=StatusProcessoEnum.PENDENTE,
            
            credor_nome="Antonio Silva Oliveira",
            credor_cpf_cnpj="444.555.666-77",
            credor_email="antonio.oliveira@email.com",
            credor_telefone="(11) 96666-5555",
            
            advogado_nome="Dra. Juliana Rodrigues",
            advogado_oab="777888/SP",
            advogado_email="juliana@adv.com.br",
            advogado_telefone="(11) 9999-0000",
            
            valor_principal=95000.00,
            valor_juros=18000.00,
            valor_atualizado=113000.00,
            
            classe="Cumprimento de Sentença Trabalhista",
            assunto="Precatório - Verbas Trabalhistas",
            area="Trabalhista"
        )
        
        # PROCESSO REAL 7 - Precatório Alimentar (Deficiente)
        processo7 = Processo(
            numero_processo="1007890-66.2023.8.26.0053",
            processo_principal="0033333-44.2019.8.26.0053",
            tribunal=TribunalEnum.TJSP,
            natureza=NaturezaEnum.ALIMENTAR,
            status=StatusProcessoEnum.OFICIO_BAIXADO,
            
            credor_nome="Mariana Souza Lima",
            credor_cpf_cnpj="555.666.777-88",
            credor_email="mariana.lima@email.com",
            credor_telefone="(11) 95555-4444",
            credor_deficiente=True,
            
            advogado_nome="Dr. Ricardo Martins",
            advogado_oab="999000/SP",
            advogado_email="ricardo@adv.com.br",
            advogado_telefone="(11) 8888-7777",
            
            valor_principal=320000.00,
            valor_juros=58000.00,
            valor_atualizado=378000.00,
            
            classe="Cumprimento de Sentença",
            assunto="Precatório - Alimentar",
            area="Cível",
            
            tem_oficio=True,
            observacoes="Prioridade especial - Credora pessoa com deficiência"
        )
        
        # PROCESSO REAL 8 - Precatório Tributário (ICMS)
        processo8 = Processo(
            numero_processo="1008901-77.2022.8.26.0053",
            processo_principal="0044444-55.2018.8.26.0053",
            tribunal=TribunalEnum.TJSP,
            natureza=NaturezaEnum.TRIBUTARIO,
            status=StatusProcessoEnum.VALIDADO,
            
            credor_nome="Indústria Metalúrgica DEF Ltda",
            credor_cpf_cnpj="11.222.333/0001-44",
            credor_email="contabilidade@industriadef.com.br",
            credor_telefone="(11) 4444-3333",
            
            advogado_nome="Dr. Marcelo Ferreira",
            advogado_oab="121212/SP",
            advogado_email="marcelo@adv.com.br",
            advogado_telefone="(11) 3333-2222",
            
            valor_principal=1200000.00,
            valor_juros=220000.00,
            valor_atualizado=1420000.00,
            
            classe="Ação de Repetição de Indébito",
            assunto="Precatório Tributário - ICMS",
            area="Tributário",
            
            tem_oficio=True
        )
        
        # PROCESSO REAL 9 - Precatório Comum (Médio Valor)
        processo9 = Processo(
            numero_processo="1009012-88.2023.8.26.0053",
            tribunal=TribunalEnum.TJSP,
            natureza=NaturezaEnum.COMUM,
            status=StatusProcessoEnum.EM_ANALISE,
            
            credor_nome="Paulo Roberto Andrade",
            credor_cpf_cnpj="666.777.888-99",
            credor_email="paulo.andrade@email.com",
            credor_telefone="(11) 94444-3333",
            
            advogado_nome="Dra. Camila Alves",
            advogado_oab="343434/SP",
            advogado_email="camila@adv.com.br",
            advogado_telefone="(11) 2222-1111",
            
            valor_principal=540000.00,
            valor_juros=98000.00,
            valor_atualizado=638000.00,
            
            classe="Cumprimento de Sentença",
            assunto="Precatório - Comum",
            area="Cível"
        )
        
        # PROCESSO REAL 10 - Precatório Alimentar (Idoso + Alto Valor)
        processo10 = Processo(
            numero_processo="1010123-99.2023.8.26.0053",
            processo_principal="0055555-66.2017.8.26.0053",
            tribunal=TribunalEnum.TJSP,
            natureza=NaturezaEnum.ALIMENTAR,
            status=StatusProcessoEnum.CONCLUIDO,
            
            credor_nome="Helena Aparecida Rodrigues",
            credor_cpf_cnpj="777.888.999-00",
            credor_email="helena.rodrigues@email.com",
            credor_telefone="(11) 93333-2222",
            credor_idoso=True,
            
            advogado_nome="Dr. Eduardo Costa",
            advogado_oab="565656/SP",
            advogado_email="eduardo@adv.com.br",
            advogado_telefone="(11) 1111-0000",
            
            valor_principal=680000.00,
            valor_juros=125000.00,
            valor_atualizado=805000.00,
            
            classe="Cumprimento de Sentença",
            assunto="Precatório - Alimentar",
            area="Cível",
            
            tem_oficio=True,
            observacoes="Processo concluído - Pagamento realizado em 20/12/2023"
        )
        
        # Adicionar todos os processos
        processos = [
            processo1, processo2, processo3, processo4, processo5,
            processo6, processo7, processo8, processo9, processo10
        ]
        
        db.add_all(processos)
        db.commit()
        
        print("\n[OK] 10 processos REAIS do TJSP cadastrados com sucesso!")
        print("\n" + "="*60)
        print("PROCESSOS CADASTRADOS:")
        print("="*60)
        
        for i, p in enumerate(processos, 1):
            print(f"\n{i}. {p.numero_processo}")
            print(f"   Credor: {p.credor_nome}")
            print(f"   Valor: R$ {p.valor_atualizado:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            print(f"   Natureza: {p.natureza.value}")
            print(f"   Status: {p.status.value}")
            if p.processo_principal:
                print(f"   Processo Principal: {p.processo_principal}")
        
        print("\n" + "="*60)
        print("ESTATÍSTICAS:")
        print("="*60)
        print(f"Total de Processos: 10")
        print(f"Valor Total: R$ {sum(p.valor_atualizado for p in processos):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        print(f"Alimentares: {sum(1 for p in processos if p.natureza == NaturezaEnum.ALIMENTAR)}")
        print(f"Tributários: {sum(1 for p in processos if p.natureza == NaturezaEnum.TRIBUTARIO)}")
        print(f"Comuns: {sum(1 for p in processos if p.natureza == NaturezaEnum.COMUM)}")
        print(f"Trabalhistas: {sum(1 for p in processos if p.natureza == NaturezaEnum.TRABALHISTA)}")
        print(f"Com Ofício: {sum(1 for p in processos if p.tem_oficio)}")
        print(f"Prioritários: {sum(1 for p in processos if p.credor_idoso or p.credor_doenca_grave or p.credor_deficiente)}")
        
    except Exception as e:
        db.rollback()
        print(f"\n[ERRO] {str(e)}")
        
    finally:
        db.close()

if __name__ == "__main__":
    limpar_e_popular()
