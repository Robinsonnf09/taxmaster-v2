@'
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import sys
sys.path.append("src")
from database import SessionLocal, Processo
from sqlalchemy import func, or_

st.set_page_config(page_title="TaxMaster CRM", page_icon="📊", layout="wide")

# Conectar ao banco
@st.cache_resource
def get_db_session():
    return SessionLocal()

db = get_db_session()

st.title("🏛️ TaxMaster CRM - Dashboard Executivo")

# ============================================
# BARRA LATERAL DE FILTROS
# ============================================
st.sidebar.header("🔍 Filtros Avançados")

# Filtro: Tribunal
tribunais_disponiveis = [t[0] for t in db.query(Processo.tribunal).distinct().all() if t[0]]
tribunais_disponiveis.insert(0, "Todos")
tribunal_selecionado = st.sidebar.selectbox("Tribunal", tribunais_disponiveis)

# Filtro: Valor (Range)
st.sidebar.subheader("💰 Faixa de Valor")
valor_min = st.sidebar.number_input("Valor Mínimo (R$)", min_value=0, value=0, step=100000)
valor_max = st.sidebar.number_input("Valor Máximo (R$)", min_value=0, value=10000000, step=100000)

# Filtro: Natureza
st.sidebar.subheader("📋 Natureza")
natureza_input = st.sidebar.text_input("Natureza (ex: Alimentar, Tributário)")

# Filtro: Data de Expedição
st.sidebar.subheader("📅 Data de Expedição")
col1, col2 = st.sidebar.columns(2)
with col1:
    data_inicio = st.date_input("De", value=datetime.now() - timedelta(days=365))
with col2:
    data_fim = st.date_input("Até", value=datetime.now())

# Filtro: Número do Processo
st.sidebar.subheader("🔢 Número do Processo")
numero_processo_busca = st.sidebar.text_input("Número do Processo")

# Filtro: Score Mínimo
score_minimo = st.sidebar.slider("Score Mínimo", 0.0, 10.0, 0.0, 0.1)

# Botão de Buscar
buscar = st.sidebar.button("🔍 Aplicar Filtros", type="primary", use_container_width=True)

# Botão de Limpar Filtros
if st.sidebar.button("🔄 Limpar Filtros", use_container_width=True):
    st.rerun()

st.sidebar.divider()

# ============================================
# APLICAR FILTROS NA QUERY
# ============================================
query = db.query(Processo)

# Aplicar filtro de tribunal
if tribunal_selecionado != "Todos":
    query = query.filter(Processo.tribunal == tribunal_selecionado)

# Aplicar filtro de valor
if valor_min > 0:
    query = query.filter(Processo.valor_atualizado >= valor_min)
if valor_max > 0:
    query = query.filter(Processo.valor_atualizado <= valor_max)

# Aplicar filtro de natureza
if natureza_input:
    query = query.filter(Processo.natureza.ilike(f"%{natureza_input}%"))

# Aplicar filtro de data de expedição
if data_inicio and data_fim:
    query = query.filter(
        Processo.data_expedicao >= datetime.combine(data_inicio, datetime.min.time()),
        Processo.data_expedicao <= datetime.combine(data_fim, datetime.max.time())
    )

# Aplicar filtro de número do processo
if numero_processo_busca:
    query = query.filter(Processo.numero_processo.ilike(f"%{numero_processo_busca}%"))

# Aplicar filtro de score
if score_minimo > 0:
    query = query.filter(Processo.score_oportunidade >= score_minimo)

# Executar query
processos_filtrados = query.all()
total_filtrado = len(processos_filtrados)

# ============================================
# MÉTRICAS PRINCIPAIS
# ============================================
col1, col2, col3, col4 = st.columns(4)

total_processos = db.query(Processo).count()
valor_total_filtrado = sum([p.valor_atualizado or 0 for p in processos_filtrados])
processos_hoje = db.query(Processo).filter(
    func.date(Processo.created_at) == datetime.now().date()
).count()

with col1:
    st.metric("Processos Filtrados", f"{total_filtrado:,}", f"de {total_processos:,}")

with col2:
    st.metric("Valor Total Filtrado", f"R$ {valor_total_filtrado/1_000_000:.1f}M")

with col3:
    leads_filtrados = len([p for p in processos_filtrados if p.score_oportunidade and p.score_oportunidade >= 8.0])
    st.metric("Leads Qualificados", leads_filtrados)

with col4:
    st.metric("Novos Hoje", processos_hoje)

st.divider()

# ============================================
# TABELA DE RESULTADOS COM BUSCA DE OFÍCIO
# ============================================
st.subheader("📋 Resultados da Busca")

if processos_filtrados:
    # Criar DataFrame
    df_resultados = pd.DataFrame([
        {
            "Tribunal": p.tribunal,
            "Número do Processo": p.numero_processo,
            "Credor": p.credor_nome or "N/A",
            "Valor Principal": f"R$ {p.valor_principal:,.2f}" if p.valor_principal else "N/A",
            "Valor Atualizado": f"R$ {p.valor_atualizado:,.2f}" if p.valor_atualizado else "N/A",
            "Fase": p.fase or "N/A",
            "Natureza": p.natureza or "N/A",
            "Data Expedição": p.data_expedicao.strftime("%d/%m/%Y") if p.data_expedicao else "N/A",
            "Score": f"{p.score_oportunidade:.1f}" if p.score_oportunidade else "N/A",
            "ID": p.id
        }
        for p in processos_filtrados
    ])
    
    # Exibir tabela
    st.dataframe(
        df_resultados.drop(columns=["ID"]),
        use_container_width=True,
        hide_index=True
    )
    
    # ============================================
    # BUSCAR OFÍCIO REQUISITÓRIO
    # ============================================
    st.divider()
    st.subheader("📄 Buscar Ofício Requisitório")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        processo_selecionado = st.selectbox(
            "Selecione um processo para buscar o ofício",
            options=df_resultados["Número do Processo"].tolist(),
            index=0
        )
    
    with col2:
        st.write("")
        st.write("")
        if st.button("🔍 Buscar Ofício", type="primary", use_container_width=True):
            # Buscar processo no banco
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
                        st.write("**Valor Principal:**", f"R$ {processo.valor_principal:,.2f}" if processo.valor_principal else "N/A")
                        st.write("**Valor Atualizado:**", f"R$ {processo.valor_atualizado:,.2f}" if processo.valor_atualizado else "N/A")
                        st.write("**Fase:**", processo.fase or "N/A")
                        st.write("**Prioridade:**", processo.prioridade or "N/A")
                    
                    with col3:
                        st.write("**Score:**", f"{processo.score_oportunidade:.1f}/10" if processo.score_oportunidade else "N/A")
                        st.write("**Risco:**", processo.risco or "N/A")
                        st.write("**Deságio Sugerido:**", f"{processo.desagio_sugerido:.1f}%" if processo.desagio_sugerido else "N/A")
                        st.write("**Data Expedição:**", processo.data_expedicao.strftime("%d/%m/%Y") if processo.data_expedicao else "N/A")
                
                # Simular busca de ofício (aqui você implementaria a lógica real)
                st.info("🤖 Iniciando busca automática do ofício requisitório...")
                
                import time
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                    if i < 30:
                        status_text.text("Acessando portal do tribunal...")
                    elif i < 60:
                        status_text.text("Buscando processo no sistema...")
                    elif i < 90:
                        status_text.text("Localizando ofício requisitório...")
                    else:
                        status_text.text("Finalizando busca...")
                
                # Resultado simulado
                st.success("✅ Ofício requisitório localizado!")
                
                st.download_button(
                    label="📥 Baixar Ofício Requisitório (PDF)",
                    data=b"Conteudo simulado do oficio requisitorio",
                    file_name=f"oficio_{processo.numero_processo.replace('/', '_')}.pdf",
                    mime="application/pdf"
                )
                
                st.warning("⚠️ **Nota:** Esta é uma simulação. Na versão real, o robô acessará o portal do tribunal e fará o download do ofício automaticamente.")
            else:
                st.error("❌ Processo não encontrado no banco de dados")
    
    # ============================================
    # EXPORTAR RESULTADOS
    # ============================================
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv = df_resultados.drop(columns=["ID"]).to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Exportar CSV",
            data=csv,
            file_name=f"processos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        excel_buffer = pd.ExcelWriter("temp.xlsx", engine='openpyxl')
        df_resultados.drop(columns=["ID"]).to_excel(excel_buffer, index=False)
        excel_buffer.close()
        
        with open("temp.xlsx", "rb") as f:
            st.download_button(
                label="📥 Exportar Excel",
                data=f,
                file_name=f"processos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    
    with col3:
        st.button("📧 Enviar por Email", use_container_width=True)

else:
    st.info("🔍 Nenhum processo encontrado com os filtros aplicados. Tente ajustar os critérios de busca.")

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
            title="Processos por Tribunal"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💰 Distribuição por Valor")
        valores = [p.valor_atualizado or 0 for p in processos_filtrados]
        fig = px.histogram(
            valores,
            nbins=10,
            title="Distribuição de Valores",
            labels={"value": "Valor (R$)", "count": "Quantidade"}
        )
        st.plotly_chart(fig, use_container_width=True)

# ============================================
# RODAPÉ
# ============================================
st.divider()
st.caption(f"TaxMaster CRM v1.0 | Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
'@ | Out-File -FilePath "dashboard/app_filtros.py" -Encoding UTF8

Write-Host "[OK] Dashboard com filtros avançados criado!" -ForegroundColor Green
Write-Host "`nExecute:" -ForegroundColor Cyan
Write-Host "python -m streamlit run dashboard/app_filtros.py" -ForegroundColor White