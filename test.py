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
        # 1. Carga das bases do Evento (PostgreSQL exportado)
        df_chegadas = pd.read_csv('base_chegadas.csv')
        df_compras = pd.read_csv('base_compras.csv')
        df_ociosos = pd.read_csv('base_ociosos.csv')
        df_forn = pd.read_csv('base_fornecedores.csv')
        df_global = pd.read_csv('base_global_metas.csv')

        # 2. Carga Segura do ERP (WinThor)
        df_erp = pd.read_csv(
            'dados_conexao_condicao_26.csv', 
            sep=';', 
            encoding='latin-1', 
            on_bad_lines='warn'
        )
        
        # =========================================================
        # 3. DATA QUALITY: HIGIENIZAÇÃO DE CABEÇALHOS
        # =========================================================
        # Remove espaços nas pontas e destrói os caracteres invisíveis (BOM do Excel/Windows)
        df_erp.columns = df_erp.columns.str.strip().str.replace('ï»¿', '').str.replace('\ufeff', '')
        
        # Trava de Segurança (Fail-Fast)
        if 'CODFILIAL' not in df_erp.columns:
            st.error("🚨 Erro de Schema: Coluna 'CODFILIAL' não encontrada no arquivo WinThor.")
            st.warning(f"O Pandas enxergou estas colunas: {list(df_erp.columns)}")
            st.info("Dica: Verifique se o arquivo está salvo com separador Ponto e Vírgula (;) e não Vírgula (,).")
            st.stop()
            
        # =========================================================
        # 4. ENRIQUECIMENTO GEOGRÁFICO
        # =========================================================
        # Dicionário de Tradução (Filial -> UF)
        mapa_filiais = {
            1: 'CE', 2: 'PI', 3: 'CE', 4: 'MA', 5: 'MA',
            6: 'PI', 7: 'BA', 8: 'PE', 9: 'PE'
        }
        
        # Converte a filial para numérico antes de mapear para garantir o "match"
        df_erp['CODFILIAL'] = pd.to_numeric(df_erp['CODFILIAL'], errors='coerce').fillna(0).astype(int)
        
        # Traduz a filial para o Estado correspondente
        df_erp['ESTADO'] = df_erp['CODFILIAL'].map(mapa_filiais)

        # =========================================================
        # 5. TRATAMENTO FINANCEIRO (Localização Numérica)
        # =========================================================
        # Passo A: Garante que é lido como texto e troca a vírgula (BR) pelo ponto (US)
        df_erp['TOTAL_FATURADO'] = df_erp['TOTAL_FATURADO'].astype(str).str.replace(',', '.', regex=False)
        df_erp['VALOR_DEVOLVIDO'] = df_erp['VALOR_DEVOLVIDO'].astype(str).str.replace(',', '.', regex=False)
        
        # Passo B: Converte para numérico de forma segura e preenche nulos com zero
        df_erp['TOTAL_FATURADO'] = pd.to_numeric(df_erp['TOTAL_FATURADO'], errors='coerce').fillna(0)
        df_erp['VALOR_DEVOLVIDO'] = pd.to_numeric(df_erp['VALOR_DEVOLVIDO'], errors='coerce').fillna(0)
        
        # Passo C: Cálculo do Faturamento Líquido
        df_erp['FATURAMENTO_LIQUIDO'] = df_erp['TOTAL_FATURADO'] - df_erp['VALOR_DEVOLVIDO']
        
        # =========================================================
        # 6. HIGIENIZAÇÃO DE CHAVES PRIMÁRIAS (Data Governance)
        # =========================================================
        # Garante que os IDs sejam lidos como números inteiros puros para o Join perfeito
        df_erp['CNPJ_FORNECEDOR'] = pd.to_numeric(df_erp['CNPJ_FORNECEDOR'], errors='coerce').fillna(0).astype(int)
        
        # ✨ CORREÇÃO AQUI: Lendo a coluna correta da sua nova planilha
        df_erp['COD_CLIENTE'] = pd.to_numeric(df_erp['COD_CLIENTE'], errors='coerce').fillna(0).astype(int) 
        
        df_forn['fornecedor_id'] = pd.to_numeric(df_forn['fornecedor_id'], errors='coerce').fillna(0).astype(int)

        return df_chegadas, df_compras, df_ociosos, df_forn, df_global, df_erp
        
    except FileNotFoundError:
        st.error("Arquivos CSV não encontrados. Certifique-se de que todas as bases estão na mesma pasta do script.")
        st.stop()

df_chegadas, df_compras, df_ociosos, df_rank, df_rank_global, df_erp = carregar_dados()

# ==============================================================================
# 3. MOTOR DE FILTROS GLOBAIS
# ==============================================================================
st.sidebar.header("🎯 Filtros Globais")

estados_unicos = pd.concat([df_chegadas['estado'], df_ociosos['estado']]).dropna().unique()
estados_unicos = sorted(list(estados_unicos))

estados_selecionados = st.sidebar.multiselect(
    "Filtrar por Estado (UF):",
    options=estados_unicos,
    default=[],
    help="Deixe vazio para visualizar todos os estados."
)

def aplicar_filtro_pandas(df, coluna):
    if not estados_selecionados or df.empty or coluna not in df.columns:
        return df
    return df[df[coluna].isin(estados_selecionados)]

df_chegadas_filtrado = aplicar_filtro_pandas(df_chegadas, 'estado')
df_compras_filtrado = aplicar_filtro_pandas(df_compras, 'estado')
df_ociosos_filtrado = aplicar_filtro_pandas(df_ociosos, 'estado')
df_rank_filtrado = aplicar_filtro_pandas(df_rank, 'estado')
df_erp_filtrado = aplicar_filtro_pandas(df_erp, 'ESTADO')

# ==============================================================================
# 4. INTERFACE E DASHBOARDS
# ==============================================================================
c_head, c_act = st.columns([5, 1])
c_head.title("🚀 Command Center: Resultados Consolidados")
if c_act.button("🔄 Recarregar CSVs"):
    st.cache_data.clear() 
    st.rerun()

t_chegadas, t_conversoes, t_ociosos, t_fornecedores, t_metas, t_auditoria, t_auditoria_clientes = st.tabs([
    "📥 Visão Geral (Chegadas)", 
    "✅ Clientes (Compraram)", 
    "⚠️ Oportunidades (Ociosos)", 
    "🏆 Fornecedores",
    "🎯 Apuração de Metas",
    "⚖️ Auditoria (ERP)",
    "👥 Auditoria (Clientes)" 
])

# --- ABA 1: CHEGADAS ---
with t_chegadas:
    if not df_chegadas_filtrado.empty:
        df_chegadas_filtrado['Tempo Decorrido'] = df_chegadas_filtrado['segundos'].apply(format_time)
        m1, m2 = st.columns(2)
        m1.metric("Grupos Econômicos no Evento", len(df_chegadas_filtrado))
        m2.metric("Total de Lojas Presentes", df_chegadas_filtrado['qtd_lojas_presentes'].sum())
        st.dataframe(df_chegadas_filtrado[['cod_cli_princ', 'estado', 'nome_grupo_representante', 'qtd_lojas_presentes', 'primeira_chegada', 'Tempo Decorrido']], use_container_width=True, hide_index=True)
    else: st.info("Nenhum dado encontrado.")

# --- ABA 2: COMPRAS ---
with t_conversoes:
    if not df_compras_filtrado.empty:
        total_soma = df_compras_filtrado['total_comprado_grupo'].sum()
        st.metric("Volume Negociado Total", formatar_moeda(total_soma))
        df_compras_filtrado['total_exibicao'] = df_compras_filtrado['total_comprado_grupo'].apply(formatar_moeda)
        st.dataframe(df_compras_filtrado, use_container_width=True, hide_index=True, column_config={"total_comprado_grupo": None})
    else: st.warning("Nenhum pedido processado.")

# --- ABA 3: OCIOSOS ---
with t_ociosos:
    if not df_ociosos_filtrado.empty:
        df_ociosos_filtrado['Tempo sem comprar'] = df_ociosos_filtrado['segundos'].apply(format_time)
        st.error(f"{len(df_ociosos_filtrado)} grupos econômicos ociosos.")
        st.dataframe(df_ociosos_filtrado[['cod_cli_princ', 'estado', 'nome_grupo', 'hora_chegada', 'Tempo sem comprar']], use_container_width=True, hide_index=True)
    else: st.success("100% de conversão!")

# --- ABA 4: FORNECEDORES ---
with t_fornecedores:
    if not df_rank_filtrado.empty:
        c_chart, c_table = st.columns([1, 1])
        with c_chart:
            df_g = df_rank_filtrado.groupby(['fornecedor'], as_index=False)['faturamento_total'].sum().sort_values(by='faturamento_total', ascending=False)
            st.plotly_chart(px.bar(df_g, x='fornecedor', y='faturamento_total', title="Faturamento por Parceiro", color='faturamento_total', color_continuous_scale='Blues'), use_container_width=True)
        with c_table:
            df_rank_filtrado['faturamento_exibicao'] = df_rank_filtrado['faturamento_total'].apply(formatar_moeda)
            st.dataframe(df_rank_filtrado, use_container_width=True, hide_index=True, column_config={"faturamento_total": None, "fornecedor_id": None})
    else: st.info("Aguardando negócios.")

# --- ABA 5: METAS ---
with t_metas:
    st.markdown("### 🎯 Tracking de Atingimento Global")
    df_metas = pd.DataFrame(meta_fornecedor)
    if not df_rank_global.empty:
        df_apuracao = pd.merge(df_metas, df_rank_global, on='fornecedor_id', how='outer')
        mapa_nomes = df_rank[['fornecedor_id', 'fornecedor']].drop_duplicates().set_index('fornecedor_id')['fornecedor']
        df_apuracao['nome_fantasia'] = df_apuracao['nome_fantasia'].fillna(df_apuracao['fornecedor_id'].map(mapa_nomes))
        df_apuracao['faturamento_total'] = df_apuracao['faturamento_total'].fillna(0)
        df_apuracao['pct_atingido'] = (df_apuracao['faturamento_total'] / df_apuracao['valor_meta']) * 100
        df_apuracao['gap'] = df_apuracao['valor_meta'] - df_apuracao['faturamento_total']
        df_apuracao['gap'] = df_apuracao['gap'].apply(lambda x: 0 if pd.notna(x) and x < 0 else x)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Meta Global", formatar_moeda(df_apuracao['valor_meta'].sum()))
        m2.metric("Realizado Geral", formatar_moeda(df_apuracao['faturamento_total'].sum()))
        m3.metric("Atingimento", f"{(df_apuracao['faturamento_total'].sum()/df_apuracao['valor_meta'].sum()*100):.1f}%")
        
        df_apuracao['Meta_Str'] = df_apuracao['valor_meta'].apply(lambda x: formatar_moeda(x) if pd.notna(x) else "-")
        df_apuracao['Realizado_Str'] = df_apuracao['faturamento_total'].apply(formatar_moeda)
        df_apuracao['Falta_Str'] = df_apuracao['gap'].apply(lambda x: formatar_moeda(x) if pd.notna(x) else "-")
        df_apuracao['ordem_pct'] = df_apuracao['pct_atingido'].fillna(-1)
        df_apuracao = df_apuracao.sort_values(by=['ordem_pct', 'faturamento_total'], ascending=[False, False])
        
        st.dataframe(df_apuracao, use_container_width=True, hide_index=True, column_config={"nome_fantasia": "Parceiro", "Meta_Str": "Meta", "Realizado_Str": "Realizado", "pct_atingido": st.column_config.ProgressColumn("%", format="%.1f%%", min_value=0, max_value=100), "Falta_Str": "Gap", "fornecedor_id": None, "fornecedor": None, "valor_meta": None, "faturamento_total": None, "gap": None, "ordem_pct": None})

# --- ABA 6: AUDITORIA ---
with t_auditoria:
    st.markdown("### ⚖️ Reconciliação Financeira: Evento vs. WinThor")
    if not df_erp_filtrado.empty and not df_rank_filtrado.empty:
        
        df_evento_audit = df_rank_filtrado.groupby('fornecedor_id', as_index=False).agg({'fornecedor': 'first', 'faturamento_total': 'sum'})
        df_winthor_audit = df_erp_filtrado.groupby('CNPJ_FORNECEDOR', as_index=False).agg({'FORNECEDOR': 'first', 'TOTAL_FATURADO': 'sum', 'VALOR_DEVOLVIDO': 'sum', 'FATURAMENTO_LIQUIDO': 'sum'})
        df_winthor_audit.rename(columns={'CNPJ_FORNECEDOR': 'fornecedor_id'}, inplace=True)
        
        df_audit = pd.merge(df_evento_audit, df_winthor_audit, on='fornecedor_id', how='outer')
        
        # ✨ CORREÇÃO APLICADA AQUI: Tratamento explícito apenas nas colunas numéricas
        df_audit.fillna({
            'faturamento_total': 0, 
            'TOTAL_FATURADO': 0, 
            'VALOR_DEVOLVIDO': 0, 
            'FATURAMENTO_LIQUIDO': 0
        }, inplace=True)
        
        # Consolida o nome do Parceiro
        df_audit['Parceiro'] = df_audit['fornecedor'].fillna(df_audit['FORNECEDOR'])
        
        # Cálculos de Auditoria
        df_audit['Quebra'] = df_audit['faturamento_total'] - df_audit['FATURAMENTO_LIQUIDO']
        df_audit['Taxa'] = (df_audit['FATURAMENTO_LIQUIDO'] / df_audit['faturamento_total'] * 100).replace([float('inf')], 100).fillna(0)

        c1, c2, c3 = st.columns(3)
        c1.metric("Pedidos Evento", formatar_moeda(df_audit['faturamento_total'].sum()))
        c2.metric("Faturado WinThor", formatar_moeda(df_audit['FATURAMENTO_LIQUIDO'].sum()))
        c3.metric("Conversão", f"{(df_audit['FATURAMENTO_LIQUIDO'].sum()/df_audit['faturamento_total'].sum()*100):.1f}%")

        df_audit['P_Ev'] = df_audit['faturamento_total'].apply(formatar_moeda)
        df_audit['W_Liq'] = df_audit['FATURAMENTO_LIQUIDO'].apply(formatar_moeda)
        df_audit['Gap'] = df_audit['Quebra'].apply(formatar_moeda)
        
        st.dataframe(
            df_audit.sort_values(by='faturamento_total', ascending=False), 
            use_container_width=True, hide_index=True, 
            column_config={
                "fornecedor_id": "ID", "Parceiro": "Parceiro", 
                "P_Ev": "Evento", "W_Liq": "WinThor", "Gap": "Quebra", 
                "Taxa": st.column_config.ProgressColumn("Conversão", format="%.1f%%", min_value=0, max_value=100), 
                "fornecedor": None, "FORNECEDOR": None, "faturamento_total": None, 
                "TOTAL_FATURADO": None, "VALOR_DEVOLVIDO": None, "FATURAMENTO_LIQUIDO": None, "Quebra": None
            }
        )
    else: 
        st.info("Dados ERP não disponíveis.")


# --- ABA 7: AUDITORIA DETALHADA POR CLIENTE ---
with t_auditoria_clientes:
    st.markdown("### 👥 Auditoria de Conversão por Grupo Econômico")
    
    if not df_erp_filtrado.empty and not df_compras_filtrado.empty:
        # 1. Base Evento
        df_ev = df_compras_filtrado.groupby('cod_cli_princ', as_index=False).agg({
            'nome_grupo_representante': 'first',
            'estado': 'first',
            'total_comprado_grupo': 'sum'
        })
        df_ev['cod_cli_princ'] = pd.to_numeric(df_ev['cod_cli_princ'], errors='coerce').fillna(0).astype(int)

        # 2. Base WinThor (Agrupando por COD_CLIENTE)
        df_wt = df_erp_filtrado.groupby('COD_CLIENTE', as_index=False).agg({
            'CLIENTE': 'first',
            'FATURAMENTO_LIQUIDO': 'sum',
            'CNPJ_FORNECEDOR': 'nunique',
            'CODFILIAL': 'first'
        })
        df_wt.rename(columns={'COD_CLIENTE': 'cod_cli_princ'}, inplace=True)
        df_wt['cod_cli_princ'] = pd.to_numeric(df_wt['cod_cli_princ'], errors='coerce').fillna(0).astype(int)

        # 3. Join Final
        df_final = pd.merge(df_ev, df_wt, on='cod_cli_princ', how='outer')
        df_final = df_final[df_final['cod_cli_princ'] != 0]

        # 4. Tratamento e Nome Final
        df_final.fillna({'total_comprado_grupo': 0, 'FATURAMENTO_LIQUIDO': 0, 'CNPJ_FORNECEDOR': 0}, inplace=True)
        
        # ✨ RESGATE DO NOME: Prioriza o nome do evento, se não houver, pega o do WinThor
        df_final['Nome_Final'] = df_final['nome_grupo_representante'].fillna(df_final['CLIENTE']).str.upper()
        
        df_final['Taxa'] = (df_final['FATURAMENTO_LIQUIDO'] / df_final['total_comprado_grupo'] * 100).replace([float('inf')], 100).fillna(0)

        # 5. KPIs de Topo
        total_evento = df_final['total_comprado_grupo'].sum()
        total_winthor = df_final['FATURAMENTO_LIQUIDO'].sum()
        conversao_geral = (total_winthor / total_evento * 100) if total_evento > 0 else 0
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Venda Evento", formatar_moeda(total_evento))
        c2.metric("Total Faturado WinThor", formatar_moeda(total_winthor))
        c3.metric("Conversão Global da Carteira", f"{conversao_geral:.1f}%")

        st.divider()

        # 6. Preparação das Strings de Moeda
        df_final['Ev_Str'] = df_final['total_comprado_grupo'].apply(formatar_moeda)
        df_final['Wt_Str'] = df_final['FATURAMENTO_LIQUIDO'].apply(formatar_moeda)
        
        df_display = df_final.sort_values(by='total_comprado_grupo', ascending=False)

        # 7. Exibição com o Nome do Cliente Ativado
        st.dataframe(
            df_display,
            use_container_width=True, 
            hide_index=True, 
            column_config={
                "cod_cli_princ": "Cód. Matriz",
                "Nome_Final": st.column_config.TextColumn("Grupo Econômico", width="large"), 
                "CNPJ_FORNECEDOR": st.column_config.NumberColumn("Qtd. Ind.", format="%d"),
                "CODFILIAL": "Filial",
                "Taxa": st.column_config.ProgressColumn("Aprovação", format="%.1f%%", min_value=0, max_value=100),
                "Ev_Str": "Venda Evento",
                "Wt_Str": "Faturamento WinThor",
                
                # Ocultando lixo técnico
                "nome_grupo_representante": None,
                "estado": None,
                "CLIENTE": None,
                "total_comprado_grupo": None,
                "FATURAMENTO_LIQUIDO": None
            }
        )
    else:
        st.info("Aguardando dados de faturamento para auditoria de clientes.")