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
    .stApp { background-color: #f8f9fa; }
    
    .card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 15px;
        border-left: 5px solid #2e7d32;
    }
    
    .marca-nome { color: #1b5e20; font-size: 1.2rem; font-weight: 700; margin-bottom: 5px; }
    .info-secundaria { color: #6c757d; font-size: 0.85rem; margin-bottom: 2px; }
    .lote-badge { 
        background-color: #e8f5e9; color: #2e7d32; 
        padding: 2px 8px; border-radius: 5px; font-weight: 600; font-size: 0.8rem;
    }
    
    .saldo-container {
        display: flex; justify-content: space-between; align-items: center;
        margin-top: 15px; padding-top: 10px; border-top: 1px solid #f1f1f1;
    }
    .saldo-label { color: #495057; font-weight: 500; font-size: 0.9rem; }
    .saldo-valor { color: #1565c0; font-weight: 800; font-size: 1.4rem; }

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
        st.markdown("## 🌱 Filtros")
        
        with st.form("filtros_form"):
            reg = st.selectbox("Regional", ["TODOS"] + sorted(df['Departamento Regional'].unique().tolist()))
            cid = st.selectbox("Cidade", ["TODOS"] + sorted(df['Município'].unique().tolist()))
            emp = st.selectbox("Empresa", ["TODOS"] + sorted(df['Empresa'].unique().tolist()))
            f_marca = st.text_input("Produto", placeholder="Nome do produto...")
            f_lote = st.text_input("Nº do Lote")
            check_pos = st.toggle("Apenas com saldo", value=True)
            
            btn_buscar = st.form_submit_button("CONSULTAR AGORA")
        
        if st.button("Limpar Filtros"):
            st.rerun()

    # --- ÁREA PRINCIPAL ---
    st.markdown("<h2 style='color: #2e7d32;'>🌱 Estoque Consolidado BN</h2>", unsafe_allow_html=True)
    
    if btn_buscar:
        res = df.copy()
        
        # Filtros aplicados passo a passo (mais seguro contra erros)
        if reg != "TODOS":
            res = res[res['Departamento Regional'] == reg]
        if cid != "TODOS":
            res = res[res['Município'] == cid]
        if emp != "TODOS":
            res = res[res['Empresa'] == emp]
        if f_marca:
            res = res[res['Marca Comercial'].astype(str).str.contains(f_marca, case=False)]
        if f_lote:
            res = res[res['Nº do Lote'].astype(str).str.contains(f_lote, case=False)]
        if check_pos:
            res = res[res['Saldo'] > 0]
        
        # Métricas de resumo
        c1, c2 = st.columns(2)
        c1.metric("Itens Encontrados", len(res))
        c2.metric("Saldo Total", f"{int(res['Saldo'].sum())}")
        
        st.divider()
        
        if res.empty:
            st.info("Nenhum item encontrado.")
        else:
            for _, linha in res.iterrows():
                st.markdown(f"""
                <div class="card">
                    <div class="marca-nome">{linha['Marca Comercial']}</div>
                    <div class="info-secundaria">📦 {linha['Descrição da Embalagem']}</div>
                    <div style="margin-top: 8px;">
                        <span class="lote-badge">Lote: {linha['Nº do Lote']}</span>
                    </div>
                    <div class="info-secundaria" style="margin-top: 10px;">
                        🏢 {linha['Empresa']} | 📍 {linha['Município']}
                    </div>
                    <div class="saldo-container">
                        <span class="saldo-label">SALDO DISPONÍVEL</span>
                        <span class="saldo-valor">{int(linha['Saldo'])}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("👈 Use os filtros na barra lateral e clique em 'CONSULTAR AGORA'.")
        
else:
    st.error("Erro ao carregar a planilha. Verifique o compartilhamento no Google Sheets.")
