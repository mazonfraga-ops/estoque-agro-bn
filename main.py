import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Estoque Agro BN", layout="centered", page_icon="🌱")

# Título visual
st.markdown("<h1 style='text-align: center; color: #2e7d32;'>🌱 Consulta de Estoque Agro BN</h1>", unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        df = pd.read_excel("Tabela de estoque teste.xlsx")
        # Limpar nomes de colunas (remover espaços)
        df.columns = [str(c).strip() for c in df.columns]
        # Garantir que o Saldo é número
        df['Saldo'] = pd.to_numeric(df['Saldo'], errors='coerce').fillna(0)
        return df
    except Exception as e:
        return None

df = load_data()

if df is not None:
    st.write("### Painel de Filtros")
    
    # Criando colunas para os filtros ficarem organizados
    col1, col2 = st.columns(2)
    
    with col1:
        reg = st.selectbox("📍 Regional", ["TODOS"] + sorted(df['Departamento Regional'].unique().tolist()))
        empresa = st.selectbox("🏢 Empresa", ["TODOS"] + sorted(df['Empresa'].unique().tolist()))
        lote = st.text_input("🔢 Nº do Lote")

    with col2:
        cid = st.selectbox("🏙️ Município", ["TODOS"] + sorted(df['Município'].unique().tolist()))
        marca = st.text_input("📦 Marca / Produto")
        apenas_estoque = st.checkbox("Mostrar apenas com saldo", value=True)

    # Lógica de Filtragem
    res = df.copy()
    if reg != "TODOS": res = res[res['Departamento Regional'] == reg]
    if cid != "TODOS": res = res[res['Município'] == cid]
    if empresa != "TODOS": res = res[res['Empresa'] == empresa]
    if marca: res = res[res['Marca Comercial'].str.contains(marca, case=False, na=False)]
    if lote: res = res[res['Nº do Lote'].astype(str).str.contains(lote, case=False, na=False)]
    if apenas_estoque: res = res[res['Saldo'] > 0]

    # Exibição do Resultado
    st.divider()
    st.metric("Total de Itens Encontrados", len(res))
    st.write(f"**Saldo Total Acumulado:** {int(res['Saldo'].sum())}")

    # Cards de resultados
    for _, linha in res.iterrows():
        with st.container():
            st.markdown(f"""
            <div style='border: 1px solid #e0e0e0; padding: 15px; border-radius: 10px; margin-bottom: 12px; background-color: #ffffff; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);'>
                <div style='color: #2e7d32; font-size: 18px; font-weight: bold;'>{linha['Marca Comercial']}</div>
                <div style='font-size: 14px; color: #666;'>{linha['Descrição da Embalagem']}</div>
                <hr style='margin: 8px 0;'>
                <div style='display: flex; justify-content: space-between;'>
                    <span><b>Regional:</b> {linha['Departamento Regional']}</span>
                    <span><b>Cidade:</b> {linha['Município']}</span>
                </div>
                <div style='display: flex; justify-content: space-between; margin-top: 5px;'>
                    <span><b>Lote:</b> {linha['Nº do Lote']}</span>
                    <span style='color: #1565c0; font-size: 18px;'><b>SALDO: {int(linha['Saldo'])}</b></span>
                </div>
                <div style='font-size: 12px; color: #999; margin-top: 5px;'>Empresa: {linha['Empresa']}</div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.error("Erro ao ler a planilha. Verifique se o nome do arquivo no GitHub está exatamente como: Tabela de estoque teste.xlsx")
