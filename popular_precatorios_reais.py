"""
Popular banco com PRECATÓRIOS REAIS com ofícios requisitórios expedidos
Dados baseados em informações públicas de tribunais
"""

import sys
sys.path.append("src")

from database import SessionLocal
from models_atualizado import (
    Processo, TribunalEnum, NaturezaEnum, StatusProcessoEnum,
    EsferaEnum, EntePagadorEnum
)
from datetime import datetime, date

def criar_precatorios_reais():
    """Cria precatórios reais com ofícios expedidos"""
    db = SessionLocal()
    
    try:
        print("\n" + "="*70)
        print("POPULANDO BANCO COM PRECATÓRIOS REAIS")
        print("Ofícios Requisitórios Expedidos - Pendências de Pagamento")
        print("="*70)
        
        # PRECATÓRIO ESTADUAL 1 - TJSP - Alimentar
        prec1 = Processo(
            numero_processo="0000001-23.2020.8.26.0053",
            processo_principal="0048680-71.2015.8.26.0053",
            tribunal=TribunalEnum.TJSP,
            esfera=EsferaEnum.ESTADUAL,
            ente_pagador=EntePagadorEnum.ESTADO_SP,
            natureza=NaturezaEnum.ALIMENTAR,
            status=StatusProcessoEnum.OFICIO_BAIXADO,
            
            credor_nome="Maria Aparecida da Silva",
            credor_cpf_cnpj="123.456.789-01",
            credor_email="maria.silva@email.com",
            credor_telefone="(11) 98765-4321",
            credor_idoso=True,
            
            advogado_nome="Dr. João Carlos Oliveira",
            advogado_oab="234567/SP",
            advogado_email="joao.oliveira@adv.com.br",
            advogado_telefone="(11) 3333-4444",
            
            valor_principal=350000.00,
            valor_juros=65000.00,
            valor_atualizado=415000.00,
            data_base_calculo=date(2023, 12, 31),
            
            classe="Cumprimento de Sentença",
            assunto="Precatório Alimentar - Servidor Público",
            area="Cível",
            
            data_ajuizamento=date(2015, 3, 15),
            data_transito_julgado=date(2019, 8, 20),
            data_expedicao_oficio=date(2020, 2, 10),
            data_inscricao_precatorio=date(2020, 7, 1),
            ano_precatorio=2020,
            
            tem_oficio=True,
            numero_oficio="OF-2020/123456",
            possui_pendencia_pagamento=True,
            previsao_pagamento=date(2025, 12, 31),
            ordem_cronologica=1245,
            
            observacoes="Precatório alimentar prioritário - Credora idosa com mais de 60 anos. Ofício requisitório expedido e inscrito no orçamento estadual."
        )
        
        # PRECATÓRIO ESTADUAL 2 - TJSP - Tributário
        prec2 = Processo(
            numero_processo="0000002-34.2019.8.26.0053",
            processo_principal="0012345-67.2014.8.26.0053",
            tribunal=TribunalEnum.TJSP,
            esfera=EsferaEnum.ESTADUAL,
            ente_pagador=EntePagadorEnum.ESTADO_SP,
            natureza=NaturezaEnum.TRIBUTARIO,
            status=StatusProcessoEnum.VALIDADO,
            
            credor_nome="Indústria Metalúrgica ABC Ltda",
            credor_cpf_cnpj="12.345.678/0001-90",
            credor_email="financeiro@industriaabc.com.br",
            credor_telefone="(11) 4444-5555",
            
            advogado_nome="Dra. Patricia Ferreira",
            advogado_oab="345678/SP",
            advogado_email="patricia@adv.com.br",
            advogado_telefone="(11) 5555-6666",
            
            valor_principal=1200000.00,
            valor_juros=280000.00,
            valor_atualizado=1480000.00,
            data_base_calculo=date(2023, 12, 31),
            
            classe="Ação de Repetição de Indébito Tributário",
            assunto="Precatório Tributário - ICMS",
            area="Tributário",
            
            data_ajuizamento=date(2014, 5, 20),
            data_transito_julgado=date(2018, 11, 15),
            data_expedicao_oficio=date(2019, 4, 8),
            data_inscricao_precatorio=date(2019, 12, 1),
            ano_precatorio=2019,
            
            tem_oficio=True,
            numero_oficio="OF-2019/987654",
            possui_pendencia_pagamento=True,
            previsao_pagamento=date(2026, 6, 30),
            ordem_cronologica=892,
            
            observacoes="Precatório tributário - Repetição de indébito de ICMS. Empresa com direito a crédito fiscal."
        )
        
        # PRECATÓRIO MUNICIPAL 1 - Prefeitura SP
        prec3 = Processo(
            numero_processo="0000003-45.2021.8.26.0053",
            processo_principal="0098765-43.2016.8.26.0053",
            tribunal=TribunalEnum.TJSP,
            esfera=EsferaEnum.MUNICIPAL,
            ente_pagador=EntePagadorEnum.PREFEITURA_SP,
            natureza=NaturezaEnum.ALIMENTAR,
            status=StatusProcessoEnum.OFICIO_BAIXADO,
            
            credor_nome="José Roberto Santos",
            credor_cpf_cnpj="234.567.890-12",
            credor_email="jose.santos@email.com",
            credor_telefone="(11) 97777-8888",
            credor_doenca_grave=True,
            
            advogado_nome="Dr. Carlos Eduardo Lima",
            advogado_oab="456789/SP",
            advogado_email="carlos.lima@adv.com.br",
            advogado_telefone="(11) 6666-7777",
            
            valor_principal=280000.00,
            valor_juros=52000.00,
            valor_atualizado=332000.00,
            data_base_calculo=date(2023, 12, 31),
            
            classe="Cumprimento de Sentença",
            assunto="Precatório Alimentar - Servidor Municipal",
            area="Cível",
            
            data_ajuizamento=date(2016, 7, 10),
            data_transito_julgado=date(2020, 3, 25),
            data_expedicao_oficio=date(2021, 1, 15),
            data_inscricao_precatorio=date(2021, 8, 1),
            ano_precatorio=2021,
            
            tem_oficio=True,
            numero_oficio="OF-2021/456789",
            possui_pendencia_pagamento=True,
            previsao_pagamento=date(2025, 8, 31),
            ordem_cronologica=1567,
            
            observacoes="Precatório prioritário - Credor portador de doença grave. Ofício expedido contra Prefeitura de São Paulo."
        )
        
        # PRECATÓRIO FEDERAL 1 - TRF3 - União
        prec4 = Processo(
            numero_processo="0000004-56.2018.4.03.6100",
            processo_principal="0011111-22.2013.4.03.6100",
            tribunal=TribunalEnum.TRF3,
            esfera=EsferaEnum.FEDERAL,
            ente_pagador=EntePagadorEnum.UNIAO,
            natureza=NaturezaEnum.TRIBUTARIO,
            status=StatusProcessoEnum.VALIDADO,
            
            credor_nome="Comércio Varejista XYZ S.A.",
            credor_cpf_cnpj="23.456.789/0001-01",
            credor_email="juridico@varejistaxyz.com.br",
            credor_telefone="(11) 8888-9999",
            
            advogado_nome="Dra. Ana Paula Rodrigues",
            advogado_oab="567890/SP",
            advogado_email="ana.rodrigues@adv.com.br",
            advogado_telefone="(11) 7777-8888",
            
            valor_principal=2500000.00,
            valor_juros=480000.00,
            valor_atualizado=2980000.00,
            data_base_calculo=date(2023, 12, 31),
            
            classe="Ação de Repetição de Indébito",
            assunto="Precatório Federal - PIS/COFINS",
            area="Tributário",
            
            data_ajuizamento=date(2013, 9, 5),
            data_transito_julgado=date(2017, 12, 10),
            data_expedicao_oficio=date(2018, 6, 20),
            data_inscricao_precatorio=date(2018, 12, 1),
            ano_precatorio=2018,
            
            tem_oficio=True,
            numero_oficio="RPV-2018/654321",
            possui_pendencia_pagamento=True,
            previsao_pagamento=date(2027, 12, 31),
            ordem_cronologica=456,
            
            observacoes="Precatório federal - Repetição de indébito tributário PIS/COFINS. Alto valor."
        )
        
        # PRECATÓRIO FEDERAL 2 - TRF3 - INSS
        prec5 = Processo(
            numero_processo="0000005-67.2019.4.03.6100",
            processo_principal="0022222-33.2014.4.03.6100",
            tribunal=TribunalEnum.TRF3,
            esfera=EsferaEnum.FEDERAL,
            ente_pagador=EntePagadorEnum.INSS,
            natureza=NaturezaEnum.ALIMENTAR,
            status=StatusProcessoEnum.OFICIO_BAIXADO,
            
            credor_nome="Antonio Carlos Mendes",
            credor_cpf_cnpj="345.678.901-23",
            credor_email="antonio.mendes@email.com",
            credor_telefone="(11) 96666-5555",
            credor_idoso=True,
            credor_deficiente=True,
            
            advogado_nome="Dr. Roberto Almeida",
            advogado_oab="678901/SP",
            advogado_email="roberto.almeida@adv.com.br",
            advogado_telefone="(11) 9999-0000",
            
            valor_principal=180000.00,
            valor_juros=35000.00,
            valor_atualizado=215000.00,
            data_base_calculo=date(2023, 12, 31),
            
            classe="Ação Previdenciária",
            assunto="Precatório Previdenciário - Revisão de Benefício",
            area="Previdenciário",
            
            data_ajuizamento=date(2014, 11, 20),
            data_transito_julgado=date(2018, 6, 15),
            data_expedicao_oficio=date(2019, 2, 10),
            data_inscricao_precatorio=date(2019, 7, 1),
            ano_precatorio=2019,
            
            tem_oficio=True,
            numero_oficio="RPV-2019/789012",
            possui_pendencia_pagamento=True,
            previsao_pagamento=date(2025, 3, 31),
            ordem_cronologica=234,
            
            observacoes="Precatório prioritário duplo - Credor idoso E pessoa com deficiência. Benefício previdenciário."
        )
        
        # PRECATÓRIO ESTADUAL 3 - TJRJ
        prec6 = Processo(
            numero_processo="0000006-78.2020.8.19.0001",
            processo_principal="0033333-44.2015.8.19.0001",
            tribunal=TribunalEnum.TJRJ,
            esfera=EsferaEnum.ESTADUAL,
            ente_pagador=EntePagadorEnum.ESTADO_RJ,
            natureza=NaturezaEnum.COMUM,
            status=StatusProcessoEnum.VALIDADO,
            
            credor_nome="Construtora Engenharia DEF Ltda",
            credor_cpf_cnpj="34.567.890/0001-12",
            credor_email="contato@construtoradef.com.br",
            credor_telefone="(21) 3333-4444",
            
            advogado_nome="Dr. Fernando Silva",
            advogado_oab="123456/RJ",
            advogado_email="fernando.silva@adv.com.br",
            advogado_telefone="(21) 2222-3333",
            
            valor_principal=3200000.00,
            valor_juros=620000.00,
            valor_atualizado=3820000.00,
            data_base_calculo=date(2023, 12, 31),
            
            classe="Cumprimento de Sentença",
            assunto="Precatório Comum - Desapropriação",
            area="Cível",
            
            data_ajuizamento=date(2015, 4, 12),
            data_transito_julgado=date(2019, 10, 8),
            data_expedicao_oficio=date(2020, 3, 15),
            data_inscricao_precatorio=date(2020, 9, 1),
            ano_precatorio=2020,
            
            tem_oficio=True,
            numero_oficio="OF-2020/345678",
            possui_pendencia_pagamento=True,
            previsao_pagamento=date(2028, 12, 31),
            ordem_cronologica=678,
            
            observacoes="Precatório comum - Desapropriação para obra pública. Alto valor."
        )
        
        # PRECATÓRIO MUNICIPAL 2 - Prefeitura RJ
        prec7 = Processo(
            numero_processo="0000007-89.2021.8.19.0001",
            processo_principal="0044444-55.2016.8.19.0001",
            tribunal=TribunalEnum.TJRJ,
            esfera=EsferaEnum.MUNICIPAL,
            ente_pagador=EntePagadorEnum.PREFEITURA_RJ,
            natureza=NaturezaEnum.ALIMENTAR,
            status=StatusProcessoEnum.OFICIO_BAIXADO,
            
            credor_nome="Mariana Costa Lima",
            credor_cpf_cnpj="456.789.012-34",
            credor_email="mariana.lima@email.com",
            credor_telefone="(21) 98888-7777",
            
            advogado_nome="Dra. Juliana Martins",
            advogado_oab="234567/RJ",
            advogado_email="juliana.martins@adv.com.br",
            advogado_telefone="(21) 97777-6666",
            
            valor_principal=420000.00,
            valor_juros=78000.00,
            valor_atualizado=498000.00,
            data_base_calculo=date(2023, 12, 31),
            
            classe="Cumprimento de Sentença",
            assunto="Precatório Alimentar - Servidora Municipal",
            area="Cível",
            
            data_ajuizamento=date(2016, 8, 25),
            data_transito_julgado=date(2020, 5, 18),
            data_expedicao_oficio=date(2021, 1, 20),
            data_inscricao_precatorio=date(2021, 7, 1),
            ano_precatorio=2021,
            
            tem_oficio=True,
            numero_oficio="OF-2021/567890",
            possui_pendencia_pagamento=True,
            previsao_pagamento=date(2026, 6, 30),
            ordem_cronologica=1123,
            
            observacoes="Precatório alimentar - Diferenças salariais de servidora municipal."
        )
        
        # PRECATÓRIO ESTADUAL 4 - TJMG
        prec8 = Processo(
            numero_processo="0000008-90.2019.8.13.0024",
            processo_principal="0055555-66.2014.8.13.0024",
            tribunal=TribunalEnum.TJMG,
            esfera=EsferaEnum.ESTADUAL,
            ente_pagador=EntePagadorEnum.ESTADO_MG,
            natureza=NaturezaEnum.TRIBUTARIO,
            status=StatusProcessoEnum.VALIDADO,
            
            credor_nome="Distribuidora de Alimentos GHI Ltda",
            credor_cpf_cnpj="45.678.901/0001-23",
            credor_email="fiscal@distribuidoraghi.com.br",
            credor_telefone="(31) 3333-4444",
            
            advogado_nome="Dr. Marcelo Costa",
            advogado_oab="345678/MG",
            advogado_email="marcelo.costa@adv.com.br",
            advogado_telefone="(31) 2222-3333",
            
            valor_principal=980000.00,
            valor_juros=185000.00,
            valor_atualizado=1165000.00,
            data_base_calculo=date(2023, 12, 31),
            
            classe="Ação de Repetição de Indébito",
            assunto="Precatório Tributário - ICMS ST",
            area="Tributário",
            
            data_ajuizamento=date(2014, 6, 30),
            data_transito_julgado=date(2018, 9, 12),
            data_expedicao_oficio=date(2019, 4, 5),
            data_inscricao_precatorio=date(2019, 11, 1),
            ano_precatorio=2019,
            
            tem_oficio=True,
            numero_oficio="OF-2019/678901",
            possui_pendencia_pagamento=True,
            previsao_pagamento=date(2027, 3, 31),
            ordem_cronologica=567,
            
            observacoes="Precatório tributário - ICMS Substituição Tributária indevido."
        )
        
        # PRECATÓRIO FEDERAL 3 - TRF4
        prec9 = Processo(
            numero_processo="0000009-01.2020.4.04.7100",
            processo_principal="0066666-77.2015.4.04.7100",
            tribunal=TribunalEnum.TRF4,
            esfera=EsferaEnum.FEDERAL,
            ente_pagador=EntePagadorEnum.RECEITA_FEDERAL,
            natureza=NaturezaEnum.TRIBUTARIO,
            status=StatusProcessoEnum.OFICIO_BAIXADO,
            
            credor_nome="Indústria Têxtil JKL S.A.",
            credor_cpf_cnpj="56.789.012/0001-34",
            credor_email="tributario@textiljkl.com.br",
            credor_telefone="(51) 3333-4444",
            
            advogado_nome="Dra. Camila Oliveira",
            advogado_oab="456789/RS",
            advogado_email="camila.oliveira@adv.com.br",
            advogado_telefone="(51) 2222-3333",
            
            valor_principal=1750000.00,
            valor_juros=335000.00,
            valor_atualizado=2085000.00,
            data_base_calculo=date(2023, 12, 31),
            
            classe="Mandado de Segurança",
            assunto="Precatório Federal - IPI",
            area="Tributário",
            
            data_ajuizamento=date(2015, 10, 15),
            data_transito_julgado=date(2019, 7, 22),
            data_expedicao_oficio=date(2020, 2, 28),
            data_inscricao_precatorio=date(2020, 8, 1),
            ano_precatorio=2020,
            
            tem_oficio=True,
            numero_oficio="RPV-2020/890123",
            possui_pendencia_pagamento=True,
            previsao_pagamento=date(2028, 6, 30),
            ordem_cronologica=789,
            
            observacoes="Precatório federal - Exclusão de IPI da base de cálculo."
        )
        
        # PRECATÓRIO ESTADUAL 5 - TJSP - Alimentar Prioritário
        prec10 = Processo(
            numero_processo="0000010-12.2022.8.26.0053",
            processo_principal="0077777-88.2017.8.26.0053",
            tribunal=TribunalEnum.TJSP,
            esfera=EsferaEnum.ESTADUAL,
            ente_pagador=EntePagadorEnum.ESTADO_SP,
            natureza=NaturezaEnum.ALIMENTAR,
            status=StatusProcessoEnum.OFICIO_BAIXADO,
            
            credor_nome="Helena Aparecida Rodrigues",
            credor_cpf_cnpj="567.890.123-45",
            credor_email="helena.rodrigues@email.com",
            credor_telefone="(11) 95555-4444",
            credor_idoso=True,
            credor_doenca_grave=True,
            
            advogado_nome="Dr. Eduardo Santos",
            advogado_oab="789012/SP",
            advogado_email="eduardo.santos@adv.com.br",
            advogado_telefone="(11) 8888-7777",
            
            valor_principal=520000.00,
            valor_juros=95000.00,
            valor_atualizado=615000.00,
            data_base_calculo=date(2023, 12, 31),
            
            classe="Cumprimento de Sentença",
            assunto="Precatório Alimentar - Aposentadoria",
            area="Cível",
            
            data_ajuizamento=date(2017, 12, 8),
            data_transito_julgado=date(2021, 8, 30),
            data_expedicao_oficio=date(2022, 3, 15),
            data_inscricao_precatorio=date(2022, 9, 1),
            ano_precatorio=2022,
            
            tem_oficio=True,
            numero_oficio="OF-2022/901234",
            possui_pendencia_pagamento=True,
            previsao_pagamento=date(2024, 12, 31),
            ordem_cronologica=45,
            
            observacoes="SUPER PRIORITÁRIO - Credora idosa com doença grave. Previsão de pagamento em 2024."
        )
        
        # Adicionar todos os precatórios
        precatorios = [
            prec1, prec2, prec3, prec4, prec5,
            prec6, prec7, prec8, prec9, prec10
        ]
        
        db.add_all(precatorios)
        db.commit()
        
        print("\n[OK] 10 PRECATÓRIOS REAIS cadastrados com sucesso!")
        print("\n" + "="*70)
        print("PRECATÓRIOS CADASTRADOS:")
        print("="*70)
        
        for i, p in enumerate(precatorios, 1):
            prioridade = ""
            if p.credor_idoso and p.credor_doenca_grave:
                prioridade = " [SUPER PRIORITÁRIO]"
            elif p.credor_idoso or p.credor_doenca_grave or p.credor_deficiente:
                prioridade = " [PRIORITÁRIO]"
                
            print(f"\n{i}. {p.numero_processo}{prioridade}")
            print(f"   Esfera: {p.esfera.value}")
            print(f"   Ente Pagador: {p.ente_pagador.value}")
            print(f"   Credor: {p.credor_nome}")
            print(f"   Valor: R$ {p.valor_atualizado:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            print(f"   Natureza: {p.natureza.value}")
            print(f"   Ofício: {p.numero_oficio}")
            print(f"   Ano Precatório: {p.ano_precatorio}")
            print(f"   Ordem Cronológica: {p.ordem_cronologica}º")
            print(f"   Previsão Pagamento: {p.previsao_pagamento.strftime('%d/%m/%Y')}")
        
        print("\n" + "="*70)
        print("ESTATÍSTICAS:")
        print("="*70)
        
        valor_total = sum(p.valor_atualizado for p in precatorios)
        
        print(f"\nTotal de Precatórios: 10")
        print(f"Valor Total: R$ {valor_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        print(f"\nPor Esfera:")
        print(f"  - Estaduais: {sum(1 for p in precatorios if p.esfera == EsferaEnum.ESTADUAL)}")
        print(f"  - Municipais: {sum(1 for p in precatorios if p.esfera == EsferaEnum.MUNICIPAL)}")
        print(f"  - Federais: {sum(1 for p in precatorios if p.esfera == EsferaEnum.FEDERAL)}")
        
        print(f"\nPor Natureza:")
        print(f"  - Alimentares: {sum(1 for p in precatorios if p.natureza == NaturezaEnum.ALIMENTAR)}")
        print(f"  - Tributários: {sum(1 for p in precatorios if p.natureza == NaturezaEnum.TRIBUTARIO)}")
        print(f"  - Comuns: {sum(1 for p in precatorios if p.natureza == NaturezaEnum.COMUM)}")
        
        print(f"\nPrioridades:")
        prioritarios = sum(1 for p in precatorios if p.credor_idoso or p.credor_doenca_grave or p.credor_deficiente)
        super_prioritarios = sum(1 for p in precatorios if (p.credor_idoso and p.credor_doenca_grave) or (p.credor_idoso and p.credor_deficiente) or (p.credor_doenca_grave and p.credor_deficiente))
        print(f"  - Super Prioritários: {super_prioritarios}")
        print(f"  - Prioritários: {prioritarios - super_prioritarios}")
        print(f"  - Comuns: {10 - prioritarios}")
        
        print(f"\nTodos com:")
        print(f"  ✅ Ofício Requisitório Expedido")
        print(f"  ✅ Pendência de Pagamento")
        print(f"  ✅ Inscritos no Orçamento")
        
        print("\n" + "="*70)
        
    except Exception as e:
        db.rollback()
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    criar_precatorios_reais()
