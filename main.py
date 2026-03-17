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

# --- ESTILO VISUAL REVISADO (LOTE E SALDO EM DESTAQUE MÁXIMO) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    
    .card {
        background-color: #ffffff;
        padding: 22px;
        border-radius: 18px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        margin-bottom: 18px;
        border-left: 6px solid #2e7d32;
    }
    
    .marca-nome { color: #1b5e20; font-size: 1.25rem; font-weight: 800; margin-bottom: 8px; }
    .info-secundaria { color: #546e7a; font-size: 0.9rem; margin-top: 4px; }
    
    /* LOTE AGORA DO TAMANHO DO SALDO (1.6rem) */
    .lote-badge { 
        background-color: #f1f8e9; 
        color: #1b5e20; 
        padding: 8px 16px; 
        border-radius: 10px; 
        font-weight: 900; 
        font-size: 1.6rem; /* Tamanho igual ao saldo solicitado */
        display: inline-block;
        border: 2px solid #c8e6c9;
        margin-top: 12px;
        margin-bottom: 12px;
        letter-spacing: 0.5px;
    }
    
    .saldo-container {
        display: flex; justify-content: space-between; align-items: center;
        margin-top: 15px; padding-top: 12px; border-top: 1px solid #f1f1f1;
    }
    .saldo-label { color: #455a64; font-weight: 600; font-size: 0.85rem; letter-spacing: 0.5px; }
    
    /* VALOR DO SALDO MANTIDO EM 1.6rem */
    .saldo-valor { color: #1565c0; font-weight: 900; font-size: 1.6rem; }
    
    div.stButton > button:first-child {
        background-color: #2e7d32; color: white; border-radius: 12px;
        border: none; padding: 0.7rem 2rem; width: 100%; font-weight: bold; font-size: 1rem;
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
        st.markdown("## 🌱 Filtros de Estoque")
        with st.form("filtros_form"):
            reg = st.selectbox("📍 Regional", ["TODOS"] + sorted(df['Departamento Regional'].unique().tolist()))
            cid = st.selectbox("🏙️ Município", ["TODOS"] + sorted(df['Município'].unique().tolist()))
            emp = st.selectbox("🏢 Empresa", ["TODOS"] + sorted(df['Empresa'].unique().tolist()))
            doc_filtro = st.selectbox("📄 Nº Documento", ["TODOS"] + sorted(df['Nº Documento'].unique().tolist()))
            emb_filtro = st.selectbox("📦 Tipo de Embalagem", ["TODOS"] + sorted(df['Descrição da Embalagem'].unique().tolist()))
            st.divider()
            f_marca = st.text_input("Busca por Produto", placeholder="Nome...")
            f_lote = st.text_input("Nº do Lote")
            check_pos = st.toggle("Apenas com saldo", value=True)
            btn_buscar = st.form_submit_button("CONSULTAR AGORA")
        
        if st.button("Limpar Tudo"):
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
                    
                    <div>
                        <span class="lote-badge">Lote: {linha['Nº do Lote']}</span>
                    </div>
                    
                    <div class="info-secundaria" style="margin-top: 5px;">
                        🏢 {linha['Empresa']}
                    </div>
                    
                    <div class="saldo-container">
                        <span class="saldo-label">SALDO DISPONÍVEL</span>
                        <span class="saldo-valor">{int(linha['Saldo'])}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("👈 Selecione os filtros ao lado e clique em 'CONSULTAR AGORA'.")
else:
    st.error("Erro ao carregar os dados. Verifique a planilha.")
