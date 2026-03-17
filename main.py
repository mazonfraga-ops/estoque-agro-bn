import streamlit as st
import pandas as pd

# Configuração da página para parecer um App
st.set_page_config(page_title="Estoque Agro BN", page_icon="🌱")

# Título e Estilo
st.markdown("<h1 style='text-align: center; color: #2e7d32;'>🌱 Estoque Agro BN</h1>", unsafe_allow_html=True)

# Função para carregar dados
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("Tabela de estoque teste.xlsx")
        df.columns = [str(c).strip() for c in df.columns]
        df['Saldo'] = pd.to_numeric(df['Saldo'], errors='coerce').fillna(0)
        return df
    except:
        return None

df = load_data()

if df is not None:
    # Filtros simples no topo
    st.write("### Filtros de Consulta")
    reg = st.selectbox("Regional", ["TODOS"] + sorted(df['Departamento Regional'].unique().tolist()))
    cid = st.selectbox("Município", ["TODOS"] + sorted(df['Município'].unique().tolist()))
    marca = st.text_input("Marca Comercial / Produto")
    
    # Lógica de Filtro
    res = df.copy()
    if reg != "TODOS": res = res[res['Departamento Regional'] == reg]
    if cid != "TODOS": res = res[res['Município'] == cid]
    if marca: res = res[res['Marca Comercial'].str.contains(marca, case=False, na=False)]
    res = res[res['Saldo'] > 0]

    st.success(f"Saldo Total: {int(res['Saldo'].sum())}")

    # Lista de resultados estilo "Card"
    for _, linha in res.iterrows():
        with st.container():
            st.markdown(f"""
            <div style='border: 1px solid #ddd; padding: 15px; border-radius: 10px; margin-bottom: 10px; background-color: #f9f9f9;'>
                <b style='color: #1b5e20; font-size: 18px;'>{linha['Marca Comercial']}</b><br>
                <small>Embalagem: {linha['Descrição da Embalagem']}</small><br>
                <small>Lote: {linha['Nº do Lote']}</small><br>
                <hr style='margin: 10px 0;'>
                <div style='display: flex; justify-content: space-between;'>
                    <span>SALDO:</span>
                    <b style='color: #0d47a1; font-size: 20px;'>{int(linha['Saldo'])}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.error("Arquivo 'Tabela de estoque teste.xlsx' não encontrado no GitHub.")
