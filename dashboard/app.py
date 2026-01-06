import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="TaxMaster CRM", page_icon="📊", layout="wide")

st.title("🏛️ TaxMaster CRM - Dashboard Executivo")

# Metricas principais
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Processos Coletados", "1.247", "+89 hoje")

with col2:
    st.metric("Valor em Estoque", "R$ 45.2M", "+R$ 2.3M")

with col3:
    st.metric("Taxa de Conversão", "89.3%", "+5.2%")

with col4:
    st.metric("Leads Qualificados", "156", "+23 hoje")

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

# Graficos
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Fluxo de Pagamentos")
    dates = pd.date_range(start="2024-01", end="2024-12", freq="MS")
    values = [2.1, 2.5, 3.2, 2.8, 3.5, 4.1, 3.8, 4.5, 5.2, 4.8, 5.5, 6.2]
    fig = px.line(x=dates, y=values, labels={"x": "Mês", "y": "Valor (R$ M)"})
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🎯 Distribuição por Tribunal")
    tribunals = ["TJRJ", "TJSP", "TJRS", "TRF1", "TRF2"]
    counts = [450, 320, 280, 150, 47]
    fig = px.pie(names=tribunals, values=counts)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Oportunidades quentes
st.subheader("🔥 Oportunidades Quentes (Hoje)")

opportunities = {
    "Tribunal": ["TJRJ", "TJSP", "TRF1"],
    "Processo": ["0001234-56.2024.8.19.0001", "1234567-89.2024.8.26.0100", "0012345-67.2024.4.01.0000"],
    "Valor": ["R$ 2.3M", "R$ 450K", "R$ 1.8M"],
    "Fase": ["Expedido hoje", "Trânsito em julgado", "Fase final"],
    "Score": [9.2, 8.7, 8.9]
}

df_opp = pd.DataFrame(opportunities)
st.dataframe(df_opp, use_container_width=True, hide_index=True)
