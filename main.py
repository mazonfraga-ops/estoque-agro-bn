import streamlit as st
import pandas as pd

# Configuração da página para Mobile
st.set_page_config(page_title="Consulta Agro BN", layout="centered", page_icon="🌱")

# Título Principal
st.markdown("<h1 style='text-align: center; color: #2e7d32;'>Estoque Consolidado BN</h1>", unsafe_allow_html=True)

@st.cache_data
def carregar_dados():
    nome_arquivo = "Tabela de estoque teste.xlsx"
    try:
        df = pd.read_excel(nome_arquivo)
        df.columns = df.columns.str.strip()
        df = df.fillna("---")
        # Garante que o Saldo seja número
        df['Saldo'] = pd.to_numeric(df['Saldo'], errors='coerce').fillna(0)
        return df
    except:
        return None

df = carregar_dados()

if df is None:
    st.error("Erro: Arquivo 'Tabela de estoque teste.xlsx' não encontrado no GitHub.")
else:
    # --- INTERFACE DE FILTROS ---
    st.write("### 🔍 Filtros em Lista")
    
    col1, col2 = st.columns(2)
    with col1:
        drop_regional = st.selectbox("Regional", ["TODOS"] + sorted(df['Departamento Regional'].unique().tolist()))
        drop_empresa = st.selectbox("Empresa", ["TODOS"] + sorted(df['Empresa'].unique().tolist()))
    with col2:
        drop_cidade = st.selectbox("Cidade", ["TODOS"] + sorted(df['Município'].unique().tolist()))
        drop_doc = st.selectbox("Nº Documento", ["TODOS"] + sorted(df['Nº Documento'].unique().tolist()))

    st.divider()
    st.write("### ⌨️ Busca por Texto")
    
    f_marca = st.text_input("Marca Comercial")
    f_embalagem = st.text_input("Descrição da Embalagem")
    f_lote = st.text_input("Nº do Lote")
    
    check_estoque_positivo = st.checkbox("Apenas saldo maior que zero", value=True)

    # --- LÓGICA DA CONSULTA ---
    res = df.copy()

    if drop_regional != "TODOS": res = res[res['Departamento Regional'] == drop_regional]
    if drop_cidade != "TODOS": res = res[res['Município'] == drop_cidade]
    if drop_empresa != "TODOS": res = res[res['Empresa'] == drop_empresa]
    if drop_doc != "TODOS": res = res[res['Nº Documento'] == drop_doc]
    
    if f_marca: res = res[res['Marca Comercial'].astype(str).str.contains(f_marca, case=False)]
    if f_embalagem: res = res[res['Descrição da Embalagem'].astype(str).str.contains(f_embalagem, case=False)]
    if f_lote: res = res[res['Nº do Lote'].astype(str).str.contains(f_lote, case=False)]
    
    if check_estoque_positivo:
        res = res[res['Saldo'] > 0]

    # --- RESULTADOS ---
    st.divider()
    total_saldo = res['Saldo'].sum()
    st.markdown(f"### Saldo Total: <span style='color:green'>{total_saldo}</span>", unsafe_allow_html=True)

    if res.empty:
        st.warning("Nenhum item encontrado com esses filtros.")
    else:
        # Mostra os primeiros 100 resultados para não travar o celular
        for _, linha in res.head(100).iterrows():
            st.markdown(f"""
            <div style='border: 1px solid #DDDDDD; padding: 15px; border-radius: 10px; margin-bottom: 10px; background-color: white;'>
                <div style='color: #2e7d32; font-weight: bold; font-size: 16px;'>{linha['Marca Comercial']}</div>
                <div style='font-size: 12px; color: #616161; font-style: italic;'>Embalagem: {linha['Descrição da Embalagem']}</div>
                <div style='font-size: 12px; font-weight: 500;'>Lote: {linha['Nº do Lote']}</div>
                <div style='font-size: 11px;'>Empresa: {linha['Empresa']}</div>
                <hr style='margin: 8px 0; border: 0; border-top: 1px solid #EEEEEE;'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <span style='font-size: 12px; color: #757575;'>SALDO ATUAL:</span>
                    <span style='color: #0d47a1; font-weight: bold; font-size: 18px;'>{linha['Saldo']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Botão de Limpar (O Streamlit limpa ao atualizar a página, mas podemos adicionar um botão se desejar)
    if st.button("LIMPAR FILTROS"):
        st.rerun()
