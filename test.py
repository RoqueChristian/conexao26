import streamlit as st
import pandas as pd
import plotly.express as px 
import locale
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

# ==============================================================================
# 1. CONFIGURAÇÃO E GOVERNANÇA DE SESSÃO
# ==============================================================================
st.set_page_config(
    page_title="Command Center - Resultados 2026",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded" 
)

# --- AUTENTICAÇÃO ---
with open('.streamlit/config_auth.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('main')

if authentication_status is False:
    st.error('❌ Usuário ou senha incorretos')
    st.stop() 
elif authentication_status is None:
    st.warning('⚠️ Insira suas credenciais para acessar o painel')
    st.stop() 

authenticator.logout('Sair', 'sidebar')
st.sidebar.write(f'👤 Usuário: *{name}*')
st.sidebar.markdown("---")

# ==============================================================================
# DICIONÁRIO DE METAS
# ==============================================================================
meta_fornecedor = [
    {"fornecedor_id": 30307, "nome_fantasia": "CCM IND E COM DE PROD DESCARTAVEIS S/A", "valor_meta": 9000000.0},
    {"fornecedor_id": 789603, "nome_fantasia": "SOFTYS BRASIL LTDA", "valor_meta": 7000000.0},
    {"fornecedor_id": 47252, "nome_fantasia": "NEOQUIMICA", "valor_meta": 6500000.0},
    {"fornecedor_id": 30791, "nome_fantasia": "LABORATORIO TEUTO BRASILEIRO S/A", "valor_meta": 3000000.0},
    {"fornecedor_id": 793120, "nome_fantasia": "HYPERA S.A", "valor_meta": 2000000.0},
    {"fornecedor_id": 33928, "nome_fantasia": "GEOLAB IND FARMACEUTICA S/A", "valor_meta": 1500000.0},
    {"fornecedor_id": 789423, "nome_fantasia": "KLEY HERTZ DISTRIBUIDORA LTDA", "valor_meta": 1500000.0},
    {"fornecedor_id": 793186, "nome_fantasia": "ACCUMED PRODUTOS MEDICO HOSPITALARES LTDA", "valor_meta": 1500000.0},
    {"fornecedor_id": 794365, "nome_fantasia": "BIOSINTETICA - ACHE - LABOFARMA PRODUTOS FARMACEUTICOS LTDA", "valor_meta": 1500000.0},
    {"fornecedor_id": 31267, "nome_fantasia": "MEDQUIMICA IND FARMACEUTICA S.", "valor_meta": 1000000.0},
    {"fornecedor_id": 796144, "nome_fantasia": "BRACELL PAPEIS NORDESTE LTDA", "valor_meta": 1000000.0},
    {"fornecedor_id": 789112, "nome_fantasia": "MILI SA", "valor_meta": 800000.0},
    {"fornecedor_id": 789228, "nome_fantasia": "SANDOZ DO BRASI  IND. FARMAC LTDA (SP)", "valor_meta": 800000.0},
    {"fornecedor_id": 792121, "nome_fantasia": "GIOVANNA BABY - PRO NOVA DIST E COM DE COSMETICOS LTDA", "valor_meta": 600000.0},
    {"fornecedor_id": 794445, "nome_fantasia": "SANOFI MEDLEY FARMACEUTICA LTDA", "valor_meta": 600000.0},
    {"fornecedor_id": 30083, "nome_fantasia": "LOLLY BABY PRODUTOS INFANTIS L", "valor_meta": 550000.0},
    {"fornecedor_id": 33057, "nome_fantasia": "NATULAB LABORATORIO LTDA", "valor_meta": 500000.0},
    {"fornecedor_id": 794671, "nome_fantasia": "PRINCIPIA ES COMERCIO DE COSMETICOS LTDA", "valor_meta": 500000.0},
    {"fornecedor_id": 77800, "nome_fantasia": "ESSITY DO BRASIL INDUSTRIA E COMERCIO LTDA", "valor_meta": 500000.0},
    {"fornecedor_id": 792141, "nome_fantasia": "TOTAL VITA - GROWUP INDUSTRIA DE ALIMENTOS E NUTRACEUTICOS LTDA", "valor_meta": 500000.0},
    {"fornecedor_id": 793261, "nome_fantasia": "FARMAX DISTRIBUIDORA S.A", "valor_meta": 500000.0},
    {"fornecedor_id": 795345, "nome_fantasia": "DINNO BABY - DIST DE COSMET BY FATTORE LTDA - EPP", "valor_meta": 500000.0},
    {"fornecedor_id": 794223, "nome_fantasia": "FALCON DISTRIBUICAO (ONTEX)", "valor_meta": 400000.0},
    {"fornecedor_id": 790080, "nome_fantasia": "BIOLAB FARMA GENERICOS LTDA", "valor_meta": 400000.0},
    {"fornecedor_id": 790283, "nome_fantasia": "PHARLAB INDUSTRIA FARMACEUTICA S.A", "valor_meta": 400000.0},
    {"fornecedor_id": 796369, "nome_fantasia": "MYRALIS INDUSTRIA FARMACEUTICA LTDA", "valor_meta": 400000.0},
    {"fornecedor_id": 790595, "nome_fantasia": "SC JOHNSON LTDA", "valor_meta": 350000.0},
    {"fornecedor_id": 794468, "nome_fantasia": "CELLERA CONSUMO LTDA (ES)", "valor_meta": 300000.0},
    {"fornecedor_id": 792019, "nome_fantasia": "TORRENT DO BRASIL LTDA", "valor_meta": 200000.0},
    {"fornecedor_id": 30105, "nome_fantasia": "ALYNE - CIGEL DISTRIBUIDORA DE COSMETI", "valor_meta": 100000.0},
    {"fornecedor_id": 32816, "nome_fantasia": "DKT DO BRASIL PROD.DE USO PESS (PRUDENCE)", "valor_meta": 50000.0},
    {"fornecedor_id": 793247, "nome_fantasia": "NATIVITA INDUSTRIA E COMERCIO LTDA", "valor_meta": 50000.0}
]

# ==============================================================================
# 2. MOTOR DE DADOS (ETL LER CSV)
# ==============================================================================
def format_time(seconds):
    if pd.isna(seconds): return "0h 0m"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours:02d}h {minutes:02d}m"

def formatar_moeda(valor):
    try:
        return locale.currency(valor, grouping=True)
    except:
        return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

@st.cache_data
def carregar_dados():
    try:
        df_chegadas = pd.read_csv('base_chegadas.csv')
        df_compras = pd.read_csv('base_compras.csv')
        df_ociosos = pd.read_csv('base_ociosos.csv')
        df_forn = pd.read_csv('base_fornecedores.csv')
        df_global = pd.read_csv('base_global_metas.csv')
        return df_chegadas, df_compras, df_ociosos, df_forn, df_global
    except FileNotFoundError:
        st.error("Arquivos CSV não encontrados. Execute o extrator.py primeiro.")
        st.stop()

# Carregamento na Memória
df_chegadas, df_compras, df_ociosos, df_rank, df_rank_global = carregar_dados()

# ==============================================================================
# 3. MOTOR DE FILTROS GLOBAIS (SIDEBAR EM MEMÓRIA)
# ==============================================================================
st.sidebar.header("🎯 Filtros Globais")

# Coleta os estados das bases lidas em vez de consultar o banco
estados_unicos = pd.concat([df_chegadas['estado'], df_ociosos['estado']]).dropna().unique()
estados_unicos = sorted(list(estados_unicos))

estados_selecionados = st.sidebar.multiselect(
    "Filtrar por Estado (UF):",
    options=estados_unicos,
    default=[],
    help="Deixe vazio para visualizar todos os estados."
)

# Filtro via Pandas
def aplicar_filtro_pandas(df, coluna='estado'):
    if not estados_selecionados or df.empty or coluna not in df.columns:
        return df
    return df[df[coluna].isin(estados_selecionados)]

df_chegadas_filtrado = aplicar_filtro_pandas(df_chegadas)
df_compras_filtrado = aplicar_filtro_pandas(df_compras)
df_ociosos_filtrado = aplicar_filtro_pandas(df_ociosos)
df_rank_filtrado = aplicar_filtro_pandas(df_rank)

# ==============================================================================
# 4. INTERFACE E DASHBOARDS (RENDERIZAÇÃO)
# ==============================================================================
c_head, c_act = st.columns([5, 1])
c_head.title("🚀 Command Center: Resultados Consolidados")
if c_act.button("🔄 Recarregar CSVs"):
    st.cache_data.clear() 
    st.rerun()

t_chegadas, t_conversoes, t_ociosos, t_fornecedores, t_metas = st.tabs([
    "📥 Visão Geral (Chegadas)", 
    "✅ Clientes (Compraram)", 
    "⚠️ Oportunidades (Ociosos)", 
    "🏆 Fornecedores",
    "🎯 Apuração de Metas" 
])

# --- ABA 1: VISÃO GERAL (CHEGADAS) ---
with t_chegadas:
    if not df_chegadas_filtrado.empty:
        df_chegadas_filtrado['Tempo Decorrido'] = df_chegadas_filtrado['segundos'].apply(format_time)
        
        m1, m2 = st.columns(2)
        m1.metric("Grupos Econômicos no Evento", len(df_chegadas_filtrado))
        m2.metric("Total de Lojas (CNPJs) Presentes", df_chegadas_filtrado['qtd_lojas_presentes'].sum())
        
        st.dataframe(
            df_chegadas_filtrado[['cod_cli_princ', 'estado', 'nome_grupo_representante', 'qtd_lojas_presentes', 'primeira_chegada', 'Tempo Decorrido']], 
            use_container_width=True, hide_index=True,
            column_config={
                "cod_cli_princ": "Cód. Matriz", "estado": "Estado",
                "nome_grupo_representante": "Grupo Econômico", "qtd_lojas_presentes": "Lojas no Evento",
                "primeira_chegada": st.column_config.TimeColumn("Primeiro Check-in", format="HH:mm")
            }
        )
    else:
        st.info("Nenhum dado encontrado para os filtros selecionados.")

# --- ABA 2: CLIENTES COM COMPRAS ---
with t_conversoes:
    if not df_compras_filtrado.empty:
        total_soma = df_compras_filtrado['total_comprado_grupo'].sum()
        st.metric("Volume Negociado Total", formatar_moeda(total_soma))
        
        df_compras_filtrado['total_exibicao'] = df_compras_filtrado['total_comprado_grupo'].apply(formatar_moeda)

        st.dataframe(
            df_compras_filtrado, 
            use_container_width=True, hide_index=True,
            column_config={
                "cod_cli_princ": "Cód. Matriz", "estado": "Estado",
                "nome_grupo_representante": "Grupo Econômico", "qtd_fornecedores": st.column_config.NumberColumn("Qtd. Fornecedores", format="%d"), 
                "total_exibicao": "Total Comprado", "fornecedores_visitados": "Fornecedores Listados",
                "total_comprado_grupo": None
            }
        )
    else:
        st.warning("Nenhum pedido processado para os filtros selecionados.")

# --- ABA 3: MAPA DE OPORTUNIDADES (OCIOSOS) ---
with t_ociosos:
    st.markdown("### 🔥 Foco Comercial: Grupos sem pedido faturado")
    if not df_ociosos_filtrado.empty:
        df_ociosos_filtrado['Tempo sem comprar'] = df_ociosos_filtrado['segundos'].apply(format_time)
        st.error(f"{len(df_ociosos_filtrado)} grupos econômicos ociosos.")
        st.dataframe(
            df_ociosos_filtrado[['cod_cli_princ', 'estado', 'nome_grupo', 'hora_chegada', 'Tempo sem comprar']], 
            use_container_width=True, hide_index=True,
            column_config={
                "cod_cli_princ": "Cód. Matriz", "estado": "Estado",
                "nome_grupo": "Grupo Econômico", "hora_chegada": st.column_config.TimeColumn("Hora de Chegada", format="HH:mm")
            }
        )
    else:
        st.success("100% de conversão (ou nenhum grupo ocioso para este estado)!")

# --- ABA 4: RANKING DE FORNECEDORES ---
with t_fornecedores:
    if not df_rank_filtrado.empty:
        c_chart, c_table = st.columns([1, 1])
        
        with c_chart:
            df_grafico = df_rank_filtrado.groupby(['fornecedor'], as_index=False)['faturamento_total'].sum()
            df_grafico = df_grafico.sort_values(by='faturamento_total', ascending=False)
            
            fig = px.bar(
                df_grafico, x='fornecedor', y='faturamento_total', 
                text_auto='.2s', title="Faturamento Consolidado por Parceiro",
                color='faturamento_total', color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with c_table:
            st.markdown("### Faturamento Detalhado (UF)")
            df_rank_filtrado['faturamento_exibicao'] = df_rank_filtrado['faturamento_total'].apply(formatar_moeda)
            st.dataframe(
                df_rank_filtrado, 
                use_container_width=True, hide_index=True,
                column_config={
                    "fornecedor_id": None, "fornecedor": "Parceiro", "estado": "UF", 
                    "faturamento_total": None, "faturamento_exibicao": "Faturamento", 
                    "grupos_atingidos": "Grupos Convertidos"
                }
            )
    else:
        st.info("Aguardando negócios para compor o ranking.")

# --- ABA 5: APURAÇÃO DE METAS ---
with t_metas:
    st.markdown("### 🎯 Tracking de Atingimento Global por Fornecedor")
    df_metas = pd.DataFrame(meta_fornecedor)
    
    if not df_rank_global.empty:
        # 1. OUTER JOIN: Traz quem tem meta e quem não tem, mas vendeu
        df_apuracao = pd.merge(df_metas, df_rank_global, on='fornecedor_id', how='outer')
        
        # 2. Resgate de Nome: Traz o nome fantasia para os fornecedores que não estavam no dicionário
        mapa_nomes = df_rank[['fornecedor_id', 'fornecedor']].drop_duplicates().set_index('fornecedor_id')['fornecedor']
        df_apuracao['nome_fantasia'] = df_apuracao['nome_fantasia'].fillna(df_apuracao['fornecedor_id'].map(mapa_nomes))
        
        # 3. Tratamento de Nulos (Realizado)
        df_apuracao['faturamento_total'] = df_apuracao['faturamento_total'].fillna(0)
        
        # 4. Cálculos Financeiros (Individual)
        df_apuracao['pct_atingido'] = (df_apuracao['faturamento_total'] / df_apuracao['valor_meta']) * 100
        df_apuracao['gap'] = df_apuracao['valor_meta'] - df_apuracao['faturamento_total']
        df_apuracao['gap'] = df_apuracao['gap'].apply(lambda x: 0 if pd.notna(x) and x < 0 else x)
        
        # 5. Formatação Condicional de Strings
        df_apuracao['Meta_Str'] = df_apuracao['valor_meta'].apply(lambda x: formatar_moeda(x) if pd.notna(x) else "-")
        df_apuracao['Realizado_Str'] = df_apuracao['faturamento_total'].apply(formatar_moeda)
        df_apuracao['Falta_Str'] = df_apuracao['gap'].apply(lambda x: formatar_moeda(x) if pd.notna(x) else "-")
        
        # 6. Ordenação
        df_apuracao['ordem_pct'] = df_apuracao['pct_atingido'].fillna(-1)
        df_apuracao = df_apuracao.sort_values(by=['ordem_pct', 'faturamento_total'], ascending=[False, False])
        df_apuracao['pct_atingido'] = df_apuracao['pct_atingido'].apply(lambda x: x if pd.notna(x) else None)
        
        # =========================================================
        # 7. KPIs GLOBAIS (ATUALIZADOS)
        # =========================================================
        # A Meta Total soma apenas os valores preenchidos no dicionário
        meta_total = df_apuracao['valor_meta'].sum()
        
        # O Realizado Total agora soma 100% das vendas da feira
        realizado_total = df_apuracao['faturamento_total'].sum()
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Meta Global do Evento", formatar_moeda(meta_total))
        m2.metric("Faturamento Realizado (Geral)", formatar_moeda(realizado_total))
        
        # O percentual global reflete o esforço de todos contra o bolsão de metas
        pct_global = (realizado_total / meta_total) * 100 if meta_total > 0 else 0
        m3.metric("Atingimento Global", f"{pct_global:.1f}%")
        # =========================================================
        
        st.divider()
        altura_tabela = (len(df_apuracao) + 1) * 35 + 10
        
        st.dataframe(
            df_apuracao,
            use_container_width=True, hide_index=True, height=altura_tabela,
            column_config={
                "fornecedor_id": None, "fornecedor": None, "valor_meta": None,
                "faturamento_total": None, "gap": None, "grupos_atingidos": None,
                "ordem_pct": None, 
                "nome_fantasia": st.column_config.TextColumn("Parceiro Estratégico", width="medium"),
                "Meta_Str": "Meta (R$)", "Realizado_Str": "Realizado (R$)",
                "pct_atingido": st.column_config.ProgressColumn(
                    "% Atingido", help="Progresso rumo ao atingimento global",
                    format="%.1f%%", min_value=0, max_value=100
                ),
                "Falta_Str": "Gap p/ Meta (R$)"
            }
        )
    else:
        st.info("Nenhum dado global disponível para apuração.")