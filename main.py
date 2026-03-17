import streamlit as st
import pandas as pd

# Link da sua planilha do Google
SHEET_URL = "https://docs.google.com/spreadsheets/d/1gQaEsLoZtldOcGsxfOM6QmH2-nnUiij-J54S0_jzugg/export?format=csv"

# Configurações de layout Pro
st.set_page_config(
    page_title="Estoque Agro BN", 
    layout="wide", 
    page_icon="🌱",
    initial_sidebar_state="expanded"
)

# --- CSS CUSTOMIZADO PARA ACABAMENTO PREMIUM ---
st.markdown("""
    <style>
    /* Fundo do App */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Estilo dos Cards de Estoque */
    .card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 15px;
        border-left: 5px solid #2e7d32;
        transition: transform 0.2s;
    }
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.12);
    }
    
    /* Títulos e Textos */
    .marca-nome { color: #1b5e20; font-size: 1.2rem; font-weight: 700; margin-bottom: 5px; }
    .info-secundaria { color: #6c757d; font-size: 0.85rem; margin-bottom: 2px; }
    .lote-badge { 
        background-color: #e8f5e9; color: #2e7d32; 
        padding: 2px 8px; border-radius: 5px; font-weight: 600; font-size: 0.8rem;
    }
    
    /* Container do Saldo */
    .saldo-container {
        display: flex; justify-content: space-between; align-items: center;
        margin-top: 15px; padding-top: 10px; border-top: 1px solid #f1f1f1;
    }
    .saldo-label { color: #495057; font-weight: 500; font-size: 0.9rem; }
    .saldo-valor { color: #1565c0; font-weight: 800; font-size: 1.4rem; }

    /* Customização de Botões */
    div.stButton > button:first-child {
        background-color: #2e7d32; color: white; border-radius: 10px;
        border: none; padding: 0.6rem 2rem; width: 100%; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=60)
def carregar_dados():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        df = df.fillna("---")
        df['Saldo'] = pd.to_numeric(df['Saldo'], errors='coerce').fillna(0)
        return df
    except:
        return None

df = carregar_dados()

if df is not None:
    # --- BARRA LATERAL (FILTROS) ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2610/2610269.png", width=80)
        st.title("Filtros de Busca")
        
        with st.form("filtros_form"):
            st.subheader("📍 Localização")
            reg = st.selectbox("Regional", ["TODOS"] + sorted(df['Departamento Regional'].unique().tolist()))
            cid = st.selectbox("Cidade", ["TODOS"] + sorted(df['Município'].unique().tolist()))
            
            st.subheader("🏢 Empresa")
            emp = st.selectbox("Selecionar", ["TODOS"] + sorted(df['Empresa'].unique().tolist()))
            
            st.subheader("📦 Produto")
            f_marca = st.text_input("Marca Comercial", placeholder="Ex: Milho...")
            f_lote = st.text_input("Nº do Lote")
            
            check_pos = st.toggle("Apenas com saldo", value=True)
            
            btn_buscar = st.form_submit_button("CONSULTAR AGORA")
        
        if st.button("Limpar Filtros"):
            st.rerun()

    # --- ÁREA PRINCIPAL ---
    st.markdown("<h2 style='color: #2e7d32;'>🌱 Estoque Consolidado BN</h2>", unsafe_allow_html=True)
    
    if btn_buscar:
        res = df.copy()
        if reg != "TODOS": res = res[res['Departamento Regional'] == reg]
        if cid != "TODOS": res = res[res['Município'] == cid]
        if emp != "TODOS": res = res[res['Empresa'] == emp]
        if f_marca: res = res[res['Marca Comercial'].astype(str).str.contains(f_marca, case=False)]
        if f_lote:
