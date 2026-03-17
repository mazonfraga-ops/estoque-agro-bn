import streamlit as st
import pandas as pd

# Link da sua planilha do Google
SHEET_URL = "https://docs.google.com/spreadsheets/d/1gQaEsLoZtldOcGsxfOM6QmH2-nnUiij-J54S0_jzugg/export?format=csv"

st.set_page_config(page_title="Consulta Agro BN", layout="centered")

# Estilo para os cards ficarem IDENTICOS ao seu Flet
st.markdown("""
    <style>
    .card {
        border: 1px solid #DDDDDD;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        background-color: white;
    }
    .titulo { color: #2e7d32; font-weight: bold; font-size: 16px; }
    .detalhe { font-size: 12px; color: #616161; font-style: italic; }
    .saldo-label { font-size: 12px; color: #757575; }
    .saldo-valor { color: #0d47a1; font-weight: bold; font-size: 18px; }
    /* Estilo do botão verde de consulta */
    div.stButton > button:first-child {
        background-color: #2e7d32;
        color: white;
        font-weight: bold;
        height: 50px;
        width: 100%;
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
    # Título exatamente como no seu Flet
    st.markdown("## Estoque Consolidado BN")
    
    # Criamos um formulário para que ele só busque quando clicar no botão (igual ao Flet)
    with st.form("meu_formulario"):
        st.markdown("**Filtros em Lista:**")
        
        # Filtros empilhados um embaixo do outro (como no seu Flet)
        reg = st.selectbox("Regional", ["TODOS"] + sorted(df['Departamento Regional'].unique().tolist()))
        cid = st.selectbox("Cidade", ["TODOS"] + sorted(df['Município'].unique().tolist()))
        emp = st.selectbox("Empresa", ["TODOS"] + sorted(df['Empresa'].unique().tolist()))
        doc = st.selectbox("Nº Documento", ["TODOS"] + sorted(df['Nº Documento'].unique().tolist()))
        
        st.divider()
        st.markdown("**Busca por Texto:**")
        
        f_marca = st.text_input("Marca Comercial")
        f_emb = st.text_input("Descrição da Embalagem")
        f_lote = st.text_input("Nº do Lote")
        
        check_pos = st.checkbox("Apenas saldo maior que zero", value=False)
        
        # Botões (Streamlit não permite Row de botões em Form facilmente, então ficam um sob o outro ou lado a lado)
        btn_consultar = st.form_submit_button("CONSULTAR ESTOQUE")

    # Botão Limpar fora do form para resetar a página
    if st.button("LIMPAR"):
        st.rerun()

    # Lógica de Filtragem após o clique
    if btn_consultar:
        res = df.copy()
        if reg != "TODOS": res = res[res['Departamento Regional'] == reg]
        if cid != "TODOS": res = res[res['Município'] == cid]
        if emp != "TODOS": res = res[res['Empresa'] == emp]
        if doc != "TODOS": res = res[res['Nº Documento'] == doc]
        if f_marca: res = res[res['Marca Comercial'].astype(str).str.contains(f_marca, case=False)]
        if f_emb: res = res[res['Descrição da Embalagem'].astype(str).str.contains(f_emb, case=False)]
        if f_lote: res = res[res['Nº do Lote'].astype(str).str.contains(f_lote, case=False)]
        if check_pos: res = res[res['Saldo'] > 0]
        
        st.divider()
        st.success(f"Saldo Total: {int(res['Saldo'].sum())}")
        
        if res.empty:
            st.error("Nenhum item encontrado.")
        else:
            for _, linha in res.iterrows():
                # Card HTML para manter o seu design
                st.markdown(f"""
                <div class="card">
                    <div class="titulo">{linha['Marca Comercial']}</div>
                    <div class="detalhe">Embalagem: {linha['Descrição da Embalagem']}</div>
                    <div style='font-size: 12px; font-weight: 500;'>Lote: {linha['Nº do Lote']}</div>
                    <div style='font-size: 11px;'>Empresa: {linha['Empresa']}</div>
                    <hr style='margin: 8px 0; border: 0; border-top: 1px solid #EEEEEE;'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <span class="saldo-label">SALDO ATUAL:</span>
                        <span class="saldo-valor">{int(linha['Saldo'])}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
else:
    st.error("Verifique o acesso da sua planilha (Qualquer pessoa com o link).")
