import streamlit as st
import pandas as pd

# 1. Link da sua planilha (ajustado para exportar como CSV automaticamente)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1gQaEsLoZtldOcGsxfOM6QmH2-nnUiij-J54S0_jzugg/export?format=csv"

st.set_page_config(page_title="Consulta Agro BN", layout="centered", page_icon="🌱")

# Estilo para os Cards
st.markdown("""
    <style>
    .estoque-card {
        border: 1px solid #DDDDDD;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        background-color: white;
    }
    .marca-titulo { color: green; font-weight: bold; font-size: 18px; }
    .saldo-valor { color: blue; font-weight: bold; font-size: 22px; }
    </style>
    """, unsafe_allow_html=True)

# O segredo da atualização automática: ttl=600 faz o app buscar dados novos a cada 10 minutos
@st.cache_data(ttl=600)
def carregar_dados():
    try:
        # Lê direto do Google Sheets
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        df = df.fillna("---")
        df['Saldo'] = pd.to_numeric(df['Saldo'], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Erro ao conectar com a planilha: {e}")
        return None

df = carregar_dados()

if df is not None:
    st.title("Estoque Consolidado BN")
    
    with st.form("filtros"):
        st.write("**Filtros em Lista:**")
        col1, col2 = st.columns(2)
        with col1:
            drop_reg = st.selectbox("Regional", ["TODOS"] + sorted(df['Departamento Regional'].unique().tolist()))
            drop_emp = st.selectbox("Empresa", ["TODOS"] + sorted(df['Empresa'].unique().tolist()))
        with col2:
            drop_cid = st.selectbox("Cidade", ["TODOS"] + sorted(df['Município'].unique().tolist()))
            drop_doc = st.selectbox("Nº Documento", ["TODOS"] + sorted(df['Nº Documento'].unique().tolist()))
            
        st.divider()
        st.write("**Busca por Texto:**")
        f_marca = st.text_input("Marca Comercial")
        f_emb = st.text_input("Descrição da Embalagem")
        f_lote = st.text_input("Nº do Lote")
        
        check_positivo = st.checkbox("Apenas saldo maior que zero", value=True)
        
        col_btn1, col_btn2 = st.columns([3, 1])
        with col_btn1:
            btn_consultar = st.form_submit_button("CONSULTAR ESTOQUE", type="primary", use_container_width=True)
        with col_btn2:
            btn_limpar = st.form_submit_button("LIMPAR", use_container_width=True)

    if btn_consultar:
        res = df.copy()
        if drop_reg != "TODOS": res = res[res['Departamento Regional'] == drop_reg]
        if drop_cid != "TODOS": res = res[res['Município'] == drop_cid]
        if drop_emp != "TODOS": res = res[res['Empresa'] == drop_emp]
        if drop_doc != "TODOS": res = res[res['Nº Documento'] == drop_doc]
        if f_marca: res = res[res['Marca Comercial'].astype(str).str.contains(f_marca, case=False)]
        if f_emb: res = res[res['Descrição da Embalagem'].astype(str).str.contains(f_emb, case=False)]
        if f_lote: res = res[res['Nº do Lote'].astype(str).str.contains(f_lote, case=False)]
        if check_positivo: res = res[res['Saldo'] > 0]
            
        st.subheader(f"Saldo Total: {int(res['Saldo'].sum())}")
        
        if res.empty:
            st.warning("Nenhum item encontrado.")
        else:
            for _, linha in res.head(100).iterrows():
                st.markdown(f"""
                <div class="estoque-card">
                    <div class="marca-titulo">{linha['Marca Comercial']}</div>
                    <div style='font-size: 13px; color: #555;'><i>Embalagem: {linha['Descrição da Embalagem']}</i></div>
                    <div style='font-size: 14px;'><b>Lote: {linha['Nº do Lote']}</b></div>
                    <div style='font-size: 12px;'>Empresa: {linha['Empresa']}</div>
                    <hr style='margin: 10px 0; border: 0.5px solid #EEE;'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <span style='font-size: 12px; color: #666;'>SALDO ATUAL:</span>
                        <span class="saldo-valor">{int(linha['Saldo'])}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
    if btn_limpar:
        st.rerun()
