import streamlit as st
import pandas as pd

# Link da sua planilha do Google (Exportada como CSV)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1gQaEsLoZtldOcGsxfOM6QmH2-nnUiij-J54S0_jzugg/export?format=csv"

# Configurações Pro
st.set_page_config(
    page_title="Estoque Agro BN", 
    layout="wide", 
    page_icon="🌱",
    initial_sidebar_state="expanded"
)

# --- ESTILO VISUAL TURBINADO ---
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    
    .card {
        background-color: #ffffff;
        padding: 22px;
        border-radius: 18px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 18px;
        border-left: 6px solid #2e7d32;
    }
    
    .marca-nome { color: #1b5e20; font-size: 1.25rem; font-weight: 800; margin-bottom: 8px; }
    .info-secundaria { color: #546e7a; font-size: 0.9rem; margin-top: 5px; }
    
    /* LOTE AINDA MAIOR E COM MAIS DESTAQUE */
    .lote-badge { 
        background-color: #f1f8e9; 
        color: #1b5e20; 
        padding: 6px 14px; 
        border-radius: 10px; 
        font-weight: 800; 
        font-size: 1.2rem; /* Aumentado para 1.2rem */
        display: inline-block;
        border: 1px solid #c8e6c9;
        letter-spacing: 0.5px;
    }
    
    .saldo-container {
        display: flex; justify-content: space-between; align-items: center;
        margin-top: 18px; padding-top: 12px; border-top: 1px solid #f0f0f0;
    }
    .saldo-label { color: #455a64; font-weight: 600; font-size: 0.85rem; letter-spacing: 1px; }
    .saldo-valor { color: #0d47a1; font-weight: 900; font-size: 1.6rem; }
    
    div.stButton > button:first-child {
        background-color: #2e7d32; color: white; border-radius: 12px;
        border: none; padding: 0.8rem; width: 100%; font-weight: bold; font-size: 1rem;
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
    with st.sidebar:
        st.markdown("## 🌱 Filtros")
        with st.form("filtros_form"):
            reg = st.selectbox("📍 Regional", ["TODOS"] + sorted(df['Departamento Regional'].unique().tolist()))
            cid = st.selectbox("🏙️ Município", ["TODOS"] + sorted(df['Município'].unique().tolist()))
            emp = st.selectbox("🏢 Empresa", ["TODOS"] + sorted(df['Empresa'].unique().tolist()))
            doc_filtro = st.selectbox("📄 Nº Documento", ["TODOS"] + sorted(df['Nº Documento'].unique().tolist()))
            emb_filtro = st.selectbox("📦 Embalagem", ["TODOS"] + sorted(df['Descrição da Embalagem'].unique().tolist()))
            st.divider()
            f_marca = st.text_input("Produto")
            f_lote = st.text_input("Nº do Lote")
            check_pos = st.toggle("Apenas com saldo", value=True)
            btn_buscar = st.form_submit_button("CONSULTAR AGORA")
        
        if st.button("Limpar"):
            st.rerun()

    st.markdown("<h2 style='color: #2e7d32;'>🌱 Estoque Consolidado BN</h2>", unsafe_allow_html=True)
    
    if btn_buscar:
        res = df.copy()
        if reg != "TODOS": res = res[res['Departamento Regional'] == reg]
        if cid != "TODOS": res = res[res['Município'] == cid]
        if emp != "TODOS": res = res[res['Empresa'] == emp]
        if doc_filtro != "TODOS": res = res[res['Nº Documento'] == doc_filtro]
        if emb_filtro != "TODOS": res = res[res['Descrição da Embalagem'] == emb_filtro]
        if f_marca: res = res[res['Marca Comercial'].astype(str).str.contains(f_marca, case=False)]
        if f_lote: res = res[res['Nº do Lote'].astype(str).str.contains(f_lote, case=False)]
        if check_pos: res = res[res['Saldo'] > 0]
        
        c1, c2 = st.columns(2)
        c1.metric("Itens", len(res))
        c2.metric("Total", f"{int(res['Saldo'].sum())}")
        
        st.divider()
        
        if res.empty:
            st.info("Nenhum item encontrado.")
        else:
            for _, linha in res.iterrows():
                st.markdown(f"""
                <div class="card">
                    <div class="marca-nome">{linha['Marca Comercial']}</div>
                    <div class="info-secundaria">📦 {linha['Descrição da Embalagem']}</div>
                    
                    <div style="margin-top: 12px; margin-bottom: 12px;">
                        <span class="lote-badge">LOTE: {linha['Nº do Lote']}</span>
                    </div>
                    
                    <div class="info-secundaria">🏢 {linha['Empresa']}</div>
                    
                    <div class="saldo-container">
                        <span class="saldo-label">SALDO DISPONÍVEL</span>
                        <span class="saldo-valor">{int(linha['Saldo'])}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("👈 Use os filtros ao lado.")
else:
    st.error("Erro ao carregar dados.")
