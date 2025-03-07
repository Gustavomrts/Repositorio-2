import streamlit as st

# Dicionário de usuários e senhas (para teste, use algo mais seguro em produção)
USERS = {"admin": "allpost123", "user": "allpost123"}

# Função de autenticação
def check_login():
    st.title("🔐 Login")
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    login_button = st.button("Entrar")

    if login_button:
        if username in USERS and USERS[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.rerun()  # Atualiza a página após login

        else:
            st.error("❌ Usuário ou senha incorretos!")

# Se não estiver logado, exibir tela de login
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    check_login()
    st.stop()  # Interrompe a execução para impedir acesso sem login

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuração da página para ocupar mais espaço
st.set_page_config(layout="wide")

# Aplicando o fundo com gradiente
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(to bottom, #004aad, #e385ec);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Definição dos parâmetros
from dotenv import load_dotenv
import os

load_dotenv()  # Carregar variáveis do .env
FB_ACCESS_TOKEN=ACCESS_TOKEN ="EAAQMPKyml7oBO6jKJEUCVfwdBC9c3NDiutPMXa78kr4ZB5Ux3iMotQaLC31TTd5OUzhjcZB1gi1xPgQ7ebk7T9JdofDcgXe6zOeM6YxrZAPIPpuDlvQwB9kVNBGkoH2rsdgFModgZBAT7HOrNxTZAZBPTAZBJItZBpZAX8yYPlfFD8TRXCgeWv3but3tl5V3aZAWZAVzzniOtgVZCl7SEf86"
FB_APP_ID=ACCOUNT_ID ="act_3675266962784994"

# Seleção de datas
data_inicial = st.date_input("Data Inicial", datetime.now().replace(day=1))
data_final = st.date_input("Data Final", datetime.now())

# Interface Streamlit
st.title("📊 ALLPOST Facebook Ads - Dashboard")
st.write("Clique no botão para carregar os dados.")

if st.button("📥 Carregar Dados", use_container_width=True):
    # Construção da URL
    API_URL = (
        f"https://graph.facebook.com/v19.0/{ACCOUNT_ID}/insights?"
        f"time_range={{'since':'{data_inicial}','until':'{data_final}'}}"
        "&level=adset&fields=campaign_name,impressions,clicks,ctr,cpc,spend,actions"
    )
    
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.get(API_URL, headers=headers)
    
    if response.status_code == 200:
        data = response.json().get("data", [])
        
        if data:
            df = pd.DataFrame(data)
            
            # Ajustando os tipos de dados
            df["impressions"] = pd.to_numeric(df["impressions"], errors='coerce').fillna(0).astype(int)
            df["clicks"] = pd.to_numeric(df["clicks"], errors='coerce').fillna(0).astype(int)
            df["ctr"] = pd.to_numeric(df["ctr"], errors='coerce').fillna(0)
            df["cpc"] = pd.to_numeric(df["cpc"], errors='coerce').fillna(0).astype(float)
            df["valor_gasto"] = pd.to_numeric(df["spend"], errors='coerce').fillna(0).astype(float)
            
            # Extraindo a métrica de "resultados"
            if "actions" in df.columns:
                def extrair_resultados(actions):
                    if isinstance(actions, list):
                        for action in actions:
                            if action.get("action_type") == "onsite_conversion.messaging_conversation_started_7d":
                                return int(action.get("value", 0))
                    return 0
                df["resultados"] = df["actions"].apply(extrair_resultados)
            else:
                df["resultados"] = 0

            # Agrupando campanhas duplicadas
            df = df.groupby("campaign_name", as_index=False).sum()
            
            # Totais
            total_gasto = df['valor_gasto'].sum()
            total_clicks = df['clicks'].sum()
            total_impressions = df['impressions'].sum()
            total_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            total_cpm = (total_gasto / total_impressions * 1000) if total_impressions > 0 else 0
            total_resultados = df['resultados'].sum()

            # Exibir métricas em caixas maiores
            st.write("### 📈 Métricas Gerais")
            col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
            
            with col7:
                 st.markdown(
        "<div style='background-color: rgba(255, 255, 255, 0.2); padding: 10px; border-radius: 10px; text-align: center;'>"
        "<h4>💰Total Gasto</h4>"
        f"<h2>R$ {total_gasto:.2f}</h2>"
        "</div>",
        unsafe_allow_html=True)
            with col5:
                st.markdown(
        "<div style='background-color: rgba(255, 255, 255, 0.2); padding: 10px; border-radius: 10px; text-align: center;'>"
        "<h4>🎯 CPC Médio</h4>"
        f"<h2>R$ {df['cpc'].mean():.2f}</h2>"
        "</div>",
        unsafe_allow_html=True)
            with col3:
                st.markdown(
        "<div style='background-color: rgba(255, 255, 255, 0.2); padding: 10px; border-radius: 10px; text-align: center;'>"
        "<h4>📊 CTR Média</h4>"
        f"<h2>{total_ctr:.2f}%</h2>"
        "</div>",
        unsafe_allow_html=True)
            with col4:
                st.markdown(
        "<div style='background-color: rgba(255, 255, 255, 0.2); padding: 10px; border-radius: 10px; text-align: center;'>"
        "<h4>👁️ Impressões</h4>"
        f"<h2>{total_impressions}</h2>"
        "</div>",
        unsafe_allow_html=True)
            with col2:
                st.markdown(
        "<div style='background-color: rgba(255, 255, 255, 0.2); padding: 10px; border-radius: 10px; text-align: center;'>"
        "<h4>🖱️ Cliques</h4>"
        f"<h2>{total_clicks}</h2>"
        "</div>",
        unsafe_allow_html=True)
            with col6:
                st.markdown(
        "<div style='background-color: rgba(255, 255, 255, 0.2); padding: 10px; border-radius: 10px; text-align: center;'>"
        "<h4>📢 CPM Médio</h4>"
        f"<h2>R$ {total_cpm:.2f}</h2>"
        "</div>",
        unsafe_allow_html=True)
            with col1:
                st.markdown(
                    """
                    <div style='background-color: rgba(255, 255, 255, 0.2); padding: 10px; border-radius: 10px; text-align: center;'>
                    <h4>📩 Conversas</h4>
                    <h2>{}</h2>
                    </div>
                    """.format(total_resultados),
                    unsafe_allow_html=True)
        

            # Tabela de Campanhas (aumentada)
            st.write("### 📌 Lista de Campanhas e Resultados")
            st.dataframe(df.drop(columns=["spend", "actions", "date_start", "date_stop"]), use_container_width=True, height=500)
            
            # Gráfico de Valor Gasto por Campanha (aumentado)
            fig_gasto = px.bar(df, x='campaign_name', y='valor_gasto', text_auto='.2f', color='campaign_name')
            fig_gasto.update_traces(textposition='outside', marker=dict(line=dict(width=1, color='black')))
            fig_gasto.update_layout(
                title='💸 Valor Gasto por Campanha',
                xaxis_title='Campanha',
                yaxis_title='Valor Gasto (R$)',
                showlegend=False,
                height=600  # Aumentando o tamanho do gráfico
            )
            st.plotly_chart(fig_gasto, use_container_width=True)

            # Gráfico de Pizza (aumentado)
            fig_pizza = go.Figure(data=[go.Pie(
                labels=df['campaign_name'], 
                values=df['clicks'], 
                hole=.3, 
                textinfo='percent+label',  # Exibe rótulos externos
                textfont_size=12,  # Aumentando fonte
                insidetextorientation='radial',
            )])
            fig_pizza.update_layout(title_text='🍕 Distribuição de Cliques por Campanha', height=500)

            # Adicionando tabela ao lado do gráfico de pizza
            st.write("### 📊 Cliques por Campanha")
            col1, col2 = st.columns([2, 1])
            with col1:
                st.plotly_chart(fig_pizza, use_container_width=True)
            with col2:
                st.dataframe(df[['campaign_name', 'clicks']].rename(columns={'campaign_name': 'Campanha', 'clicks': 'Cliques'}), height=500)
            
            import streamlit as st
            import pandas as pd
            import plotly.express as px

# Dados das cidades e estados
            locations = {
    'Cidade': ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Brasília', 'Curitiba'],
    'Estado': ['SP', 'RJ', 'MG', 'DF', 'PR'],
    'Latitude': [-23.550520, -22.906847, -19.815710, -15.780148, -25.428954],
    'Longitude': [-46.633308, -43.172896, -43.958702, -47.929222, -49.267137],
    'Atividade': [100, 150, 120, 90, 80]  # Número de interações
}

            df_locations = pd.DataFrame(locations)

# Criando um mapa focado no Brasil com tons verdes
            fig_map = px.scatter_mapbox(
    df_locations,
    lat="Latitude",
    lon="Longitude",
    text="Cidade",
    hover_name="Cidade",
    hover_data={"Estado": True, "Atividade": True},
    size="Atividade",
    color="Atividade",
    color_continuous_scale=[(0, "#4B0082"), (1, "#9400D3")],  # Escala de cores em tons verdes
    zoom=4.5,  # Ajustando o zoom para focar melhor no Brasil
    mapbox_style="open-street-map"  # Estilo verde e detalhado
)

            fig_map.update_layout(
    title="🗺️ Mapa de Atividades - Foco no Brasil 🌿",
    margin={"r":0,"t":50,"l":0,"b":0}
)

# Exibir no Streamlit
            st.write("### 🗺️ Mapa Interativo de Atividades por Estado 🌿")
            st.plotly_chart(fig_map, use_container_width=True)


        else:
            st.write("❌ Nenhum dado encontrado.")
    else:
        st.write(f"❌ Erro na requisição: {response.status_code}")
