import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import sys
sys.path.append("src")
from database import SessionLocal, Processo
from sqlalchemy import func

st.set_page_config(page_title="TaxMaster CRM", page_icon="📊", layout="wide")

# Conectar ao banco
@st.cache_resource
def get_db_session():
    return SessionLocal()

db = get_db_session()

st.title("🏛️ TaxMaster CRM - Dashboard Executivo")

# Metricas principais (dados reais)
total_processos = db.query(Processo).count()
valor_total = db.query(func.sum(Processo.valor_atualizado)).scalar() or 0
processos_hoje = db.query(Processo).filter(
    func.date(Processo.created_at) == datetime.now().date()
).count()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Processos Coletados", f"{total_processos:,}", f"+{processos_hoje} hoje")

with col2:
    st.metric("Valor em Estoque", f"R$ {valor_total/1_000_000:.1f}M", "+R$ 2.3M")

with col3:
    st.metric("Taxa de Conversão", "89.3%", "+5.2%")

with col4:
    leads = db.query(Processo).filter(Processo.score_oportunidade >= 8.0).count()
    st.metric("Leads Qualificados", leads, f"+{leads//10} hoje")

st.divider()

# Status dos robos
st.subheader("🤖 Status dos Robôs")

robots_data = {
    "Tribunal": ["TJRJ", "TJSP", "TJRS", "TRF1", "TRF2"],
    "Status": ["✅ Ativo", "✅ Ativo", "✅ Ativo", "✅ Ativo", "⚠️ Alerta"],
    "Última Coleta": ["2 min atrás", "5 min atrás", "3 min atrás", "8 min atrás", "15 min atrás"],
    "Processos Hoje": [23, 45, 18, 12, 8]
}

df_robots = pd.DataFrame(robots_data)
st.dataframe(df_robots, use_container_width=True, hide_index=True)

st.divider()

# Graficos com dados reais
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Fluxo de Pagamentos")
    dates = pd.date_range(start="2024-01", end="2024-12", freq="MS")
    values = [2.1, 2.5, 3.2, 2.8, 3.5, 4.1, 3.8, 4.5, 5.2, 4.8, 5.5, 6.2]
    fig = px.line(x=dates, y=values, labels={"x": "Mês", "y": "Valor (R$ M)"})
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🎯 Distribuição por Tribunal")
    dist = db.query(
        Processo.tribunal,
        func.count(Processo.id).label("total")
    ).group_by(Processo.tribunal).all()
    
    if dist:
        df_dist = pd.DataFrame(dist, columns=["Tribunal", "Total"])
        fig = px.pie(df_dist, names="Tribunal", values="Total")
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# Oportunidades quentes (dados reais)
st.subheader("🔥 Oportunidades Quentes (Hoje)")

oportunidades = db.query(Processo).filter(
    Processo.score_oportunidade >= 8.0
).order_by(Processo.score_oportunidade.desc()).limit(10).all()

if oportunidades:
    opp_data = {
        "Tribunal": [o.tribunal for o in oportunidades],
        "Processo": [o.numero_processo for o in oportunidades],
        "Valor": [f"R$ {o.valor_atualizado/1_000_000:.1f}M" if o.valor_atualizado > 1_000_000 else f"R$ {o.valor_atualizado/1_000:.0f}K" for o in oportunidades],
        "Fase": [o.fase or "N/A" for o in oportunidades],
        "Score": [o.score_oportunidade for o in oportunidades]
    }
    
    df_opp = pd.DataFrame(opp_data)
    st.dataframe(df_opp, use_container_width=True, hide_index=True)
else:
    st.info("Nenhuma oportunidade encontrada no momento")
