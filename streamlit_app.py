    import streamlit as st
import pandas as pd
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Votação Melhores do Ano", page_icon="🏆")

# Senha para acessar o painel administrativo
SENHA_ADMIN = "1234" 

# Nome do arquivo de banco de dados
DATA_FILE = "votos_cidade.csv"

# --- FUNÇÕES DE BANCO DE DADOS ---
def carregar_dados():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["Categoria", "Empresa", "Votos"])
        # Se não existir, cria vazio ou com exemplo básico
        df.to_csv(DATA_FILE, index=False)
        return df
    return pd.read_csv(DATA_FILE)

def salvar_no_disco(df):
    df.to_csv(DATA_FILE, index=False)

def adicionar_voto(categoria, empresa):
    df = carregar_dados()
    filtro = (df["Categoria"] == categoria) & (df["Empresa"] == empresa)
    if filtro.any():
        df.loc[filtro, "Votos"] += 1
    else:
        novo = pd.DataFrame([{"Categoria": categoria, "Empresa": empresa, "Votos": 1}])
        df = pd.concat([df, novo], ignore_index=True)
    salvar_no_disco(df)

def adicionar_empresa_admin(categoria, empresa):
    df = carregar_dados()
    # Verifica se já existe
    if not ((df["Categoria"] == categoria) & (df["Empresa"] == empresa)).any():
        novo = pd.DataFrame([{"Categoria": categoria, "Empresa": empresa, "Votos": 0}])
        df = pd.concat([df, novo], ignore_index=True)
        salvar_no_disco(df)
        return True
    return False

# --- PAINEL LATERAL (ADMINISTRATIVO) ---
with st.sidebar:
    st.header("⚙️ Configurações")
    senha_input = st.text_input("Senha de Admin", type="password")
    
    if senha_input == SENHA_ADMIN:
        st.success("Modo Administrador Ativo")
        st.markdown("---")
        
        # 1. CRIAR NOVA CATEGORIA
        st.subheader("Nova Categoria")
        nova_cat = st.text_input("Nome da Categoria (ex: Sorveteria)")
        if st.button("Criar Categoria"):
            if nova_cat:
                # Cria uma empresa "fantasma" só para registrar a categoria
                adicionar_empresa_admin(nova_cat, "Aguardando candidatos...")
                st.success(f"Categoria '{nova_cat}' criada!")
                st.rerun()

        st.markdown("---")
        
        # 2. ADICIONAR CONCORRENTE MANUALMENTE
        st.subheader("Cadastrar Concorrente")
        df_temp = carregar_dados()
        cats_disponiveis = df_temp["Categoria"].unique()
        if len(cats_disponiveis) > 0:
            cat_admin = st.selectbox("Escolha a Categoria", cats_disponiveis)
            empresa_admin = st.text_input("Nome da Empresa")
            if st.button("Cadastrar Empresa"):
                if empresa_admin:
                    if adicionar_empresa_admin(cat_admin, empresa_admin):
                        st.success("Empresa cadastrada!")
                    else:
                        st.warning("Empresa já existe.")
        
        st.markdown("---")
        # 3. BAIXAR RESULTADOS
        st.subheader("Relatórios")
        df_final = carregar_dados()
        csv = df_final.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Planilha de Votos", csv, "votos_final.csv", "text/csv")

# --- INTERFACE PRINCIPAL (O QUE O USUÁRIO VÊ) ---
st.title("🏆 Melhores do Ano")
st.markdown("Vote nas empresas que fazem a diferença na cidade!")

# Inicializa sessão
if "passo" not in st.session_state:
    st.session_state.passo = 1
if "categoria_escolhida" not in st.session_state:
    st.session_state.categoria_escolhida = ""

df = carregar_dados()
categorias_unicas = df["Categoria"].unique()

if len(categorias_unicas) == 0:
    st.info("Nenhuma votação ativa no momento. Aguarde o administrador criar as categorias.")
else:
    # FLUXO DE VOTAÇÃO (Igual ao anterior)
    if st.session_state.passo == 1:
        st.write("### Escolha uma categoria:")
        col1, col2 = st.columns(2)
        for i, cat in enumerate(categorias_unicas):
            col = col1 if i % 2 == 0 else col2
            if col.button(cat, use_container_width=True):
                st.session_state.categoria_escolhida = cat
                st.session_state.passo = 2
                st.rerun()

    elif st.session_state.passo == 2:
        cat = st.session_state.categoria_escolhida
        if st.button("⬅ Voltar"):
            st.session_state.passo = 1
            st.rerun()
            
        st.chat_message("assistant").write(f"Quem é o melhor em **{cat}**?")
        
        # Filtra e remove o placeholder "Aguardando candidatos..."
        empresas_da_cat = df[(df["Categoria"] == cat) & (df["Empresa"] != "Aguardando candidatos...")]
        lista_empresas = empresas_da_cat["Empresa"].tolist()
        
        with st.form("form_voto"):
            escolha = st.radio("Candidatos:", ["➕ ADICIONAR NOVO"] + lista_empresas)
            novo_nome = st.text_input("Se escolheu 'Adicionar Novo', digite o nome:")
            if st.form_submit_button("✅ Confirmar Voto"):
                empresa_final = novo_nome.strip().title() if escolha == "➕ ADICIONAR NOVO" and novo_nome else escolha
                if empresa_final and empresa_final != "➕ ADICIONAR NOVO":
                    adicionar_voto(cat, empresa_final)
                    st.session_state.empresa_voted = empresa_final
                    st.session_state.passo = 3
                    st.rerun()

    elif st.session_state.passo == 3:
        st.success(f"Voto confirmado para **{st.session_state.empresa_voted}**!")
        cat = st.session_state.categoria_escolhida
        df_atualizado = carregar_dados()
        dados_grafico = df_atualizado[(df_atualizado["Categoria"] == cat) & (df_atualizado["Empresa"] != "Aguardando candidatos...")].sort_values("Votos", ascending=True)
        st.bar_chart(dados_grafico, x="Votos", y="Empresa", horizontal=True, color="#FF4B4B")
        
        if st.button("🔄 Votar em outra categoria"):
            st.session_state.passo = 1
            st.rerun()
