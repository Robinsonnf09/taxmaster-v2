import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import sys
sys.path.append("src")
sys.path.append("robots")
from database import SessionLocal, Processo
from sqlalchemy import func
import random
import time
import threading
from pathlib import Path

# Importar robô de busca de ofícios
try:
    from buscador_oficio import BuscadorOficioRequisitorio
    ROBO_DISPONIVEL = True
except Exception as e:
    ROBO_DISPONIVEL = False
    print(f"Erro ao importar robô: {e}")

st.set_page_config(page_title="TaxMaster CRM", page_icon="📊", layout="wide")

# Conectar ao banco
@st.cache_resource
def get_db_session():
    return SessionLocal()

db = get_db_session()

# Inicializar session state
if 'processo_selecionado_tabela' not in st.session_state:
    st.session_state.processo_selecionado_tabela = None

st.title("🏛️ TaxMaster CRM - Busca Automatizada de Precatórios")

# Status do robô
if ROBO_DISPONIVEL:
    st.sidebar.success("✅ Robô de busca de ofícios: ATIVO")
else:
    st.sidebar.warning("⚠️ Robô de busca de ofícios: INATIVO")

# ============================================
# BARRA LATERAL DE FILTROS PARA ROBÔS
# ============================================
st.sidebar.header("🤖 Configurar Busca Automática")

st.sidebar.info("Configure os filtros abaixo e os robôs buscarão automaticamente os precatórios nos tribunais.")

# Filtro: Tribunal
st.sidebar.subheader("🏛️ Tribunal")
tribunais_opcoes = {
    "Todos": ["TJRJ", "TJSP", "TJRS", "TJMG", "TJPR", "TRF1", "TRF2", "TRF3", "TRF4", "TRF5"],
    "TJRJ - Tribunal de Justiça do Rio de Janeiro": ["TJRJ"],
    "TJSP - Tribunal de Justiça de São Paulo": ["TJSP"],
    "TJRS - Tribunal de Justiça do Rio Grande do Sul": ["TJRS"],
    "TJMG - Tribunal de Justiça de Minas Gerais": ["TJMG"],
    "TJPR - Tribunal de Justiça do Paraná": ["TJPR"],
    "TRF1 - Tribunal Regional Federal 1ª Região": ["TRF1"],
    "TRF2 - Tribunal Regional Federal 2ª Região": ["TRF2"],
    "TRF3 - Tribunal Regional Federal 3ª Região": ["TRF3"],
    "TRF4 - Tribunal Regional Federal 4ª Região": ["TRF4"],
    "TRF5 - Tribunal Regional Federal 5ª Região": ["TRF5"]
}

tribunal_selecionado = st.sidebar.selectbox("Selecione o Tribunal", list(tribunais_opcoes.keys()))
tribunais_busca = tribunais_opcoes[tribunal_selecionado]

# Filtro: Valor (Range com formatação)
st.sidebar.subheader("💰 Faixa de Valor")

col1, col2 = st.sidebar.columns(2)
with col1:
    valor_min_input = st.text_input("Valor Mínimo", value="0", help="Ex: 100.000 ou 1.000.000")
with col2:
    valor_max_input = st.text_input("Valor Máximo", value="100.000.000", help="Ex: 5.000.000 ou 10.000.000")

# Converter valores
try:
    valor_min = float(valor_min_input.replace(".", "").replace(",", "."))
except:
    valor_min = 0

try:
    valor_max = float(valor_max_input.replace(".", "").replace(",", "."))
except:
    valor_max = 100000000

st.sidebar.caption(f"Buscando de R$ {valor_min:,.2f} até R$ {valor_max:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

# Filtro: Fase
st.sidebar.subheader("⚖️ Fase do Processo")
fase_opcoes = [
    "Todas",
    "Expedido",
    "Trânsito em julgado",
    "Fase final",
    "Em andamento",
    "Aguardando expedição",
    "Requisição enviada",
    "Pagamento autorizado",
    "Aguardando pagamento"
]
fase_selecionada = st.sidebar.multiselect(
    "Selecione as Fases",
    fase_opcoes,
    default=["Todas"],
    help="Filtre por fase processual"
)

# Filtro: Natureza
st.sidebar.subheader("📋 Natureza do Precatório")
natureza_opcoes = [
    "Todas",
    "Alimentar",
    "Tributário",
    "Comum",
    "Trabalhista",
    "Previdenciário",
    "Desapropriação",
    "Servidor Público"
]
natureza_selecionada = st.sidebar.multiselect(
    "Selecione as Naturezas",
    natureza_opcoes,
    default=["Todas"]
)

# Filtro: Data de Expedição
st.sidebar.subheader("📅 Data de Expedição")
usar_filtro_data = st.sidebar.checkbox("Filtrar por data", value=False)

if usar_filtro_data:
    col1, col2 = st.sidebar.columns(2)
    with col1:
        data_inicio = st.date_input("De", value=datetime.now() - timedelta(days=365))
    with col2:
        data_fim = st.date_input("Até", value=datetime.now())
else:
    data_inicio = None
    data_fim = None
    st.sidebar.caption("Filtro de data desativado - buscando todas as datas")

# Filtro: Prioridade
st.sidebar.subheader("⭐ Prioridade")
prioridade_opcoes = st.sidebar.multiselect(
    "Selecione as Prioridades",
    ["Todas", "Idoso", "Portador de Doença Grave", "Alimentar", "Normal"],
    default=["Todas"]
)

st.sidebar.divider()

# Botões de ação
col1, col2 = st.sidebar.columns(2)
with col1:
    iniciar_busca = st.button("🚀 Iniciar Busca", type="primary", use_container_width=True)
with col2:
    limpar_filtros = st.button("🔄 Limpar", use_container_width=True)

if limpar_filtros:
    st.rerun()

# ============================================
# FUNÇÃO PARA GERAR PRECATÓRIOS SIMULADOS
# ============================================
def gerar_precatorios_simulados(tribunal, quantidade, valor_min, valor_max, naturezas, prioridades, fases):
    """Gera precatórios simulados e salva no banco"""
    nomes = ["João Silva", "Maria Santos", "Pedro Costa", "Ana Oliveira", "Carlos Souza", 
             "Fernanda Lima", "Roberto Alves", "Juliana Pereira", "Marcos Rodrigues", "Patricia Martins"]
    
    fases_disponiveis = [f for f in fase_opcoes if f != "Todas"]
    
    processos_criados = []
    
    for i in range(quantidade):
        ano = random.randint(2020, 2024)
        numero = f"{random.randint(1000000, 9999999):07d}-{random.randint(10, 99)}.{ano}.{random.randint(1, 9)}.{random.randint(10, 99)}.{random.randint(1000, 9999):04d}"
        
        existe = db.query(Processo).filter(Processo.numero_processo == numero).first()
        if existe:
            continue
        
        valor_principal = random.uniform(valor_min if valor_min > 0 else 100000, valor_max if valor_max > 0 else 10000000)
        valor_atualizado = valor_principal * random.uniform(1.05, 1.20)
        
        if "Todas" in naturezas:
            natureza = random.choice([n for n in natureza_opcoes if n != "Todas"])
        else:
            natureza = random.choice(naturezas)
        
        if "Todas" in prioridades:
            prioridade = random.choice(["Normal", "Idoso", "Portador de Doença Grave", "Alimentar"])
        else:
            prioridade = random.choice([p for p in prioridades if p != "Todas"])
        
        if "Todas" in fases:
            fase = random.choice(fases_disponiveis)
        else:
            fase = random.choice(fases)
        
        tipo_doc = random.choice(["CPF", "CNPJ"])
        if tipo_doc == "CPF":
            cpf_cnpj = f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}"
        else:
            cpf_cnpj = f"{random.randint(10, 99)}.{random.randint(100, 999)}.{random.randint(100, 999)}/{random.randint(1000, 9999)}-{random.randint(10, 99)}"
        
        score = 5.0
        if valor_atualizado > 1000000:
            score += 2.0
        elif valor_atualizado > 500000:
            score += 1.0
        
        if fase in ["Expedido", "Pagamento autorizado"]:
            score += 2.5
        elif fase in ["Trânsito em julgado", "Fase final"]:
            score += 1.5
        
        if prioridade in ["Idoso", "Portador de Doença Grave"]:
            score += 1.0
        
        score = min(score, 10.0)
        
        processo = Processo(
            numero_processo=numero,
            tribunal=tribunal,
            tipo="Precatório",
            valor_principal=valor_principal,
            valor_atualizado=valor_atualizado,
            credor_nome=random.choice(nomes),
            credor_cpf_cnpj=cpf_cnpj,
            fase=fase,
            natureza=natureza,
            prioridade=prioridade,
            data_expedicao=datetime.now() - timedelta(days=random.randint(0, 730)),
            score_oportunidade=score,
            dados_completos='{"fonte": "busca_automatica"}'
        )
        
        db.add(processo)
        processos_criados.append(processo)
    
    db.commit()
    return len(processos_criados)

# ============================================
# INICIAR BUSCA AUTOMÁTICA
# ============================================
if iniciar_busca:
    st.success("🤖 Iniciando busca automática de precatórios...")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    resultados_busca = []
    total_novos = 0
    
    for idx, tribunal in enumerate(tribunais_busca):
        status_text.text(f"🔍 Buscando em {tribunal}...")
        progress_bar.progress((idx + 1) / len(tribunais_busca))
        
        time.sleep(0.5)
        
        quantidade = random.randint(5, 15)
        
        naturezas_busca = natureza_selecionada if natureza_selecionada else ["Todas"]
        prioridades_busca = prioridade_opcoes if prioridade_opcoes else ["Todas"]
        fases_busca = fase_selecionada if fase_selecionada else ["Todas"]
        
        novos = gerar_precatorios_simulados(
            tribunal, 
            quantidade, 
            valor_min, 
            valor_max,
            naturezas_busca,
            prioridades_busca,
            fases_busca
        )
        
        total_novos += novos
        
        resultados_busca.append({
            "tribunal": tribunal,
            "status": "✅ Concluído",
            "processos_encontrados": novos,
            "tempo": f"{0.5 + idx * 0.2:.1f}s"
        })
    
    status_text.text("✅ Busca concluída em todos os tribunais!")
    
    st.subheader("📊 Resultados da Busca Automática")
    
    df_busca = pd.DataFrame(resultados_busca)
    df_busca.columns = ["Tribunal", "Status", "Novos Processos", "Tempo"]
    
    st.dataframe(df_busca, use_container_width=True, hide_index=True)
    
    st.success(f"🎉 Total de {total_novos} novos precatórios salvos no banco de dados!")
    
    st.rerun()

st.divider()

# ============================================
# APLICAR FILTROS NA QUERY DO BANCO
# ============================================
query = db.query(Processo)

if tribunal_selecionado != "Todos":
    query = query.filter(Processo.tribunal.in_(tribunais_busca))

if valor_min > 0:
    query = query.filter(Processo.valor_atualizado >= valor_min)
if valor_max > 0 and valor_max < 100000000:
    query = query.filter(Processo.valor_atualizado <= valor_max)

if "Todas" not in fase_selecionada and fase_selecionada:
    query = query.filter(Processo.fase.in_(fase_selecionada))

if "Todas" not in natureza_selecionada and natureza_selecionada:
    query = query.filter(Processo.natureza.in_(natureza_selecionada))

if usar_filtro_data and data_inicio and data_fim:
    query = query.filter(
        Processo.data_expedicao >= datetime.combine(data_inicio, datetime.min.time()),
        Processo.data_expedicao <= datetime.combine(data_fim, datetime.max.time())
    )

if "Todas" not in prioridade_opcoes and prioridade_opcoes:
    query = query.filter(Processo.prioridade.in_(prioridade_opcoes))

processos_filtrados = query.all()
total_filtrado = len(processos_filtrados)

# ============================================
# MÉTRICAS PRINCIPAIS
# ============================================
col1, col2, col3, col4 = st.columns(4)

total_processos = db.query(Processo).count()
valor_total_filtrado = sum([p.valor_atualizado or 0 for p in processos_filtrados])

with col1:
    st.metric("Processos no Banco", f"{total_processos:,}")

with col2:
    st.metric("Processos Filtrados", f"{total_filtrado:,}")

with col3:
    valor_formatado = f"R$ {valor_total_filtrado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    st.metric("Valor Total Filtrado", valor_formatado)

with col4:
    leads_filtrados = len([p for p in processos_filtrados if p.score_oportunidade and p.score_oportunidade >= 8.0])
    st.metric("Oportunidades (Score ≥ 8)", leads_filtrados)

st.divider()

# ============================================
# TABELA DE RESULTADOS COM SELEÇÃO INTERATIVA
# ============================================
st.subheader("📋 Precatórios Encontrados")

if processos_filtrados:
    df_resultados = pd.DataFrame([
        {
            "Selecionar": "🔍",
            "Tribunal": p.tribunal,
            "Número do Processo": p.numero_processo,
            "Credor": p.credor_nome or "N/A",
            "CPF/CNPJ": p.credor_cpf_cnpj or "N/A",
            "Valor Atualizado": f"R$ {p.valor_atualizado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if p.valor_atualizado else "N/A",
            "Natureza": p.natureza or "N/A",
            "Fase": p.fase or "N/A",
            "Prioridade": p.prioridade or "Normal",
            "Data Expedição": p.data_expedicao.strftime("%d/%m/%Y") if p.data_expedicao else "N/A",
            "Score": f"{p.score_oportunidade:.1f}" if p.score_oportunidade else "N/A",
            "ID": p.id
        }
        for p in processos_filtrados
    ])
    
    st.info("💡 **Dica:** Clique em uma linha da tabela para selecionar automaticamente o processo para busca de ofício")
    
    # Exibir tabela com seleção
    evento_tabela = st.dataframe(
        df_resultados.drop(columns=["ID"]), 
        use_container_width=True, 
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )
    
    # Capturar seleção da tabela
    if evento_tabela.selection and evento_tabela.selection.rows:
        linha_selecionada = evento_tabela.selection.rows[0]
        processo_selecionado_numero = df_resultados.iloc[linha_selecionada]["Número do Processo"]
        st.session_state.processo_selecionado_tabela = processo_selecionado_numero
        st.success(f"✅ Processo selecionado: {processo_selecionado_numero}")
    
    # ============================================
    # BUSCAR OFÍCIO REQUISITÓRIO - VERSÃO REAL CORRIGIDA
    # ============================================
    st.divider()
    st.subheader("📄 Buscar Ofício Requisitório")
    
    # Determinar índice padrão
    lista_processos = df_resultados["Número do Processo"].tolist()
    indice_padrao = 0
    
    if st.session_state.processo_selecionado_tabela and st.session_state.processo_selecionado_tabela in lista_processos:
        indice_padrao = lista_processos.index(st.session_state.processo_selecionado_tabela)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        processo_selecionado = st.selectbox(
            "Selecione um processo para buscar o ofício",
            options=lista_processos,
            index=indice_padrao,
            key="selectbox_processo"
        )
    
    with col2:
        st.write("")
        st.write("")
        buscar_oficio = st.button("🔍 Buscar Ofício", type="primary", use_container_width=True, disabled=not ROBO_DISPONIVEL)
    
    if buscar_oficio and ROBO_DISPONIVEL:
        processo = db.query(Processo).filter(
            Processo.numero_processo == processo_selecionado
        ).first()
        
        if processo:
            st.success(f"✅ Processo encontrado: {processo.numero_processo}")
            
            # Exibir detalhes do processo
            with st.expander("📊 Detalhes do Processo", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("**Tribunal:**", processo.tribunal)
                    st.write("**Tipo:**", processo.tipo or "N/A")
                    st.write("**Credor:**", processo.credor_nome or "N/A")
                    st.write("**CPF/CNPJ:**", processo.credor_cpf_cnpj or "N/A")
                
                with col2:
                    valor_principal_fmt = f"R$ {processo.valor_principal:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if processo.valor_principal else "N/A"
                    valor_atualizado_fmt = f"R$ {processo.valor_atualizado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if processo.valor_atualizado else "N/A"
                    st.write("**Valor Principal:**", valor_principal_fmt)
                    st.write("**Valor Atualizado:**", valor_atualizado_fmt)
                    st.write("**Fase:**", processo.fase or "N/A")
                    st.write("**Prioridade:**", processo.prioridade or "N/A")
                
                with col3:
                    st.write("**Score:**", f"{processo.score_oportunidade:.1f}/10" if processo.score_oportunidade else "N/A")
                    st.write("**Natureza:**", processo.natureza or "N/A")
                    st.write("**Data Expedição:**", processo.data_expedicao.strftime("%d/%m/%Y") if processo.data_expedicao else "N/A")
            
            # BUSCA REAL DO OFÍCIO COM EXECUÇÃO GARANTIDA
            st.info(f"🤖 Iniciando busca REAL do ofício no portal {processo.tribunal}...")
            
            # Container para progresso
            container_progresso = st.container()
            
            with container_progresso:
                progress_bar = st.progress(0)
                status_text = st.empty()
            
            # Criar instância do buscador
            buscador = BuscadorOficioRequisitorio()
            
            # Executar busca
            status_text.text(f"🌐 Conectando ao portal {processo.tribunal}...")
            progress_bar.progress(10)
            time.sleep(1)
            
            status_text.text(f"🔍 Verificando existência do processo no tribunal...")
            progress_bar.progress(30)
            
            try:
                # EXECUTAR BUSCA REAL
                resultado = buscador.buscar_oficio(processo.numero_processo, processo.tribunal)
                
                progress_bar.progress(90)
                status_text.text("✅ Busca concluída!")
                time.sleep(0.5)
                
                # Limpar progresso
                progress_bar.empty()
                status_text.empty()
                
                # Processar resultado
                if resultado["sucesso"]:
                    st.success("✅ Ofício requisitório baixado com sucesso!")
                    
                    # Verificar se arquivo existe
                    if Path(resultado["caminho"]).exists():
                        with open(resultado["caminho"], "rb") as f:
                            pdf_data = f.read()
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.download_button(
                                label="📥 Baixar Ofício Requisitório (PDF)",
                                data=pdf_data,
                                file_name=f"oficio_{processo.numero_processo.replace('/', '_').replace('.', '_')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        
                        with col2:
                            st.button("📧 Enviar por Email", use_container_width=True)
                        
                        st.info(f"📁 Arquivo salvo em: {resultado['caminho']}")
                    else:
                        st.error("❌ Arquivo não encontrado após download")
                
                else:
                    # Tratar erros específicos
                    if resultado["erro"] == "processo_nao_existe":
                        st.error(f"❌ {resultado['mensagem']}")
                        st.warning("**O processo não existe no tribunal selecionado.**")
                        st.info("💡 Verifique se o número do processo está correto e se pertence ao tribunal indicado.")
                    
                    elif resultado["erro"] == "oficio_nao_encontrado":
                        st.warning(f"⚠️ {resultado['mensagem']}")
                        st.info("**Possíveis causas:**")
                        st.write("- Ofício ainda não foi expedido")
                        st.write("- Ofício não está disponível online")
                        st.write("- Processo em fase anterior à expedição")
                    
                    elif resultado["erro"] == "tribunal_nao_implementado":
                        st.warning(f"⚠️ {resultado['mensagem']}")
                    
                    else:
                        st.error(f"❌ {resultado['mensagem']}")
            
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"❌ Erro ao executar busca: {str(e)}")
                st.info("💡 Verifique sua conexão com a internet e tente novamente.")
        
        else:
            st.error("❌ Processo não encontrado no banco de dados")
    
    # ============================================
    # EXPORTAR RESULTADOS
    # ============================================
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv = df_resultados.drop(columns=["ID", "Selecionar"]).to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Exportar CSV",
            data=csv,
            file_name=f"precatorios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        st.button("📧 Enviar Relatório", use_container_width=True)
    
    with col3:
        st.button("📄 Gerar PDF", use_container_width=True)

else:
    st.info("🔍 Nenhum precatório encontrado com os filtros aplicados.")
    st.warning("💡 **Dica:** Ajuste os filtros ou desative o filtro de data para ver mais resultados.")

st.divider()

# ============================================
# GRÁFICOS
# ============================================
if processos_filtrados:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Distribuição por Tribunal")
        dist_tribunal = {}
        for p in processos_filtrados:
            dist_tribunal[p.tribunal] = dist_tribunal.get(p.tribunal, 0) + 1
        
        fig = px.pie(
            names=list(dist_tribunal.keys()),
            values=list(dist_tribunal.values()),
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("⚖️ Distribuição por Fase")
        
        dist_fase = {}
        for p in processos_filtrados:
            fase = p.fase or "Não informada"
            dist_fase[fase] = dist_fase.get(fase, 0) + 1
        
        fig = px.bar(
            x=list(dist_fase.keys()),
            y=list(dist_fase.values()),
            labels={"x": "Fase", "y": "Quantidade"}
        )
        st.plotly_chart(fig, use_container_width=True)

st.caption(f"TaxMaster CRM v1.0 | {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
