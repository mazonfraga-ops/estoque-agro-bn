import flet as ft
import pandas as pd
import io
import requests

# 1. Link da sua planilha (ajustado para CSV)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1gQaEsLoZtldOcGsxfOM6QmH2-nnUiij-J54S0_jzugg/export?format=csv"

# Função para carregar dados ( TTL de 10 minutos para não travar o app)
# @ft.cache(ttl=600) # O Flet não tem @cache nativo como Streamlit, mas o requests é rápido
def carregar_dados_do_google():
    try:
        response = requests.get(SHEET_URL)
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            df.columns = df.columns.str.strip()
            df = df.fillna("---")
            df['Saldo'] = pd.to_numeric(df['Saldo'], errors='coerce').fillna(0)
            return df
        return None
    except:
        return None

def main(page: ft.Page):
    page.title = "Consulta Agro BN"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.ALWAYS
    page.padding = 20
    
    # Exibe carregando
    loading_text = ft.Text("Carregando banco de dados...")
    page.add(loading_text)
    page.update()

    df = carregar_dados_do_google()
    
    page.controls.remove(loading_text) # Remove o carregando

    if df is None:
        page.add(ft.Text("Erro: Não foi possível conectar à planilha.", color="red"))
        page.update()
        return

    # --- FUNÇÃO PARA CRIAR DROPDOWNS ---
    def criar_dropdown(coluna, label):
        itens = sorted(df[coluna].unique().tolist())
        opcoes = [ft.dropdown.Option("TODOS")]
        for i in itens:
            opcoes.append(ft.dropdown.Option(str(i)))
        return ft.Dropdown(label=label, options=opcoes, value="TODOS", border_radius=10, width=200)

    # Criação dos Dropdowns (width=200 para alinhar)
    drop_regional = criar_dropdown('Departamento Regional', "Regional")
    drop_cidade = criar_dropdown('Município', "Cidade")
    drop_empresa = criar_dropdown('Empresa', "Empresa")
    drop_doc = criar_dropdown('Nº Documento', "Nº Documento")
    
    f_marca = ft.TextField(label="Marca Comercial", border_radius=10)
    f_embalagem = ft.TextField(label="Descrição da Embalagem", border_radius=10)
    f_lote = ft.TextField(label="Nº do Lote", border_radius=10)
    
    check_estoque_positivo = ft.Checkbox(
        label="Apenas saldo maior que zero", 
        value=True,
        label_style=ft.TextStyle(weight="bold", color="green")
    )

    lista_resultado = ft.Column(spacing=10)
    texto_resumo = ft.Text(size=20, weight="bold", color="green")

    # Lógica de Filtragem (IGUAL ÀS SUAS REGRAS)
    def realizar_consulta(e):
        lista_resultado.controls.clear()
        res = df.copy()

        if drop_regional.value != "TODOS": res = res[res['Departamento Regional'] == drop_regional.value]
        if drop_cidade.value != "TODOS": res = res[res['Município'] == drop_cidade.value]
        if drop_empresa.value != "TODOS": res = res[res['Empresa'] == drop_empresa.value]
        if drop_doc.value != "TODOS": res = res[res['Nº Documento'] == drop_doc.value]
        
        if f_marca.value: res = res[res['Marca Comercial'].astype(str).str.contains(f_marca.value, case=False)]
        if f_embalagem.value: res = res[res['Descrição da Embalagem'].astype(str).str.contains(f_embalagem.value, case=False)]
        if f_lote.value: res = res[res['Nº do Lote'].astype(str).str.contains(f_lote.value, case=False)]
        
        if check_estoque_positivo.value:
            res = res[res['Saldo'] > 0]

        total = int(res['Saldo'].sum())
        texto_resumo.value = f"Saldo Total: {total}"

        if res.empty:
            lista_resultado.controls.append(ft.Text("Nenhum item encontrado.", color="red"))
        else:
            # Lista os primeiros 100 resultados
            for _, linha in res.head(100).iterrows():
                # MONTAGEM DO CARD (IGUAL AO SEU)
                lista_resultado.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"{linha['Marca Comercial']}", weight="bold", size=16, color="green"),
                            ft.Text(f"Embalagem: {linha['Descrição da Embalagem']}", size=12, italic=True, color="grey-700"),
                            ft.Text(f"Lote: {linha['Nº do Lote']}", size=12, weight="w500"),
                            ft.Text(f"Empresa: {linha['Empresa']}", size=11),
                            ft.Divider(height=1, color="#EEEEEE"),
                            ft.Row([
                                ft.Text("SALDO ATUAL:", size=12, color="grey-600"),
                                ft.Text(f"{int(linha['Saldo'])}", weight="bold", color="blue", size=18),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ], spacing=4),
                        bgcolor="white", 
                        padding=15, 
                        border_radius=10, 
                        border=ft.Border(ft.BorderSide(1, "#DDDDDD"), ft.BorderSide(1, "#DDDDDD"), ft.BorderSide(1, "#DDDDDD"), ft.BorderSide(1, "#DDDDDD"))
                    )
                )
        page.update()

    def limpar(e):
        drop_regional.value = drop_cidade.value = drop_empresa.value = drop_doc.value = "TODOS"
        f_marca.value = f_embalagem.value = f_lote.value = ""
        check_estoque_positivo.value = True
        lista_resultado.controls.clear()
        texto_resumo.value = ""
        page.update()

    btn_buscar = ft.Container(
        content=ft.Text("CONSULTAR ESTOQUE", color="white", weight="bold"),
        on_click=realizar_consulta,
        bgcolor="green",
        padding=15, 
        border_radius=10,
        alignment=ft.Alignment(0, 0),
        expand=True,
    )

    btn_limpar = ft.Container(
        content=ft.Text("LIMPAR"),
        on_click=limpar,
        bgcolor="#EEEEEE",
        padding=15,
        border_radius=10,
        alignment=ft.Alignment(0, 0),
        border=ft.Border(ft.BorderSide(1, "grey")),
    )

    # MONTAGEM DA PÁGINA (IGUAL AO SEU, ORGANIZADO)
    page.add(
        ft.Text("Estoque Consolidado BN", size=24, weight="bold"),
        ft.Text("Filtros em Lista:", weight="bold"),
        # Alinhando Dropdowns em Grid
        ft.Row([drop_regional, drop_cidade], alignment=ft.MainAxisAlignment.START),
        ft.Row([drop_empresa, drop_doc], alignment=ft.MainAxisAlignment.START),
        ft.Divider(),
        ft.Text("Busca por Texto:", weight="bold"),
        f_marca, f_embalagem, f_lote,
        check_estoque_positivo,
        ft.Divider(height=10, color="transparent"),
        ft.Row([btn_buscar, btn_limpar], spacing=10),
        ft.Divider(),
        texto_resumo,
        lista_resultado
    )

if __name__ == "__main__":
    ft.app(target=main)
