import streamlit as st
import datetime
import matplotlib.pyplot as plt
from src.funcs_duckdb import *
from src.funcs_ia import *


def interface_grafica():
    st.title("Projeto de Consulta e Analise de Ativos Listados na Bolsa")
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Data de Início (Default: 10 anos)", datetime.datetime.now() - datetime.timedelta(days=365*10))
    with col2:
        data_fim = st.date_input("Data de Fim (Hoje)", datetime.datetime.now())

    tickers_disponiveis = ["BTC-USD", "ETH-USD", "AAPL", "MSFT", "AMZN", "GOOGL", "FB"]
    ticker = st.multiselect("Ticker(s)", tickers_disponiveis, default=["AAPL", "MSFT", "AMZN", "GOOGL", "FB"])   # Seleção de um ou mais tickers

    @st.cache_resource
    def get_state():
        return {"state": False, "Diario": False, "Mensal": False, "Anual": False}

    state = get_state()

    if st.button("Coletar Dados e Consultar com Gen IA"):
        with st.spinner("Consulta em andamento..."):
            ingest_dados(data_inicio, data_fim, ticker)
            state['state'] = True
            st.success("Ingestão Realizada")

    if state['state']:
        periodo = st.radio("Selecione o Fechamento: ", ["Diario", "Mensal", "Anual"], index=0)
        df = consultar_fechamentos(periodo)

        st.dataframe(df)

        fig, ax = plt.subplots(figsize=(12, 6))
        for ticker, group in df.groupby("Ticker"):
            ax.plot(group["Date"], group["Close"], label=ticker, linewidth=2.5)
        ax.set_title(f"Preço de Fechamento {periodo}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Preço de Fechamento")
        ax.invert_xaxis()  # Inverter o eixo x
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

        with st.spinner("Consultando IA..."):
            st.subheader("Gemini-pro")
            if periodo == "Anual":  # Menos tokens, pode passar toda base
                st.markdown(consultar_google("[Pt-br] Analise os dados a seguir e gere insights importantes como um investidor experiente: " + df.to_string()))
            else:
                st.markdown(consultar_google("[Pt-br] Analise os dados a seguir e gere insights importantes como um investidor experiente: " + df[["Ticker", "Date", "Close"]].to_string()))
