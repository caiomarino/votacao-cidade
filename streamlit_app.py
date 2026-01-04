import streamlit as st
import pandas as pd
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Votação Melhores do Ano", page_icon="🏆")

# --- BANCO DE DADOS SIMPLES (Arquivo CSV) ---
DATA_FILE = "votos_cidade.csv"

# Função para carregar dados
def carregar_dados():
    if not os.path.exists(DATA_FILE):
        # Cria o arquivo se não existir com algumas categorias iniciais
        df = pd.DataFrame(columns=["Categoria", "Empresa", "Votos"])
        # Dados iniciais de exemplo
        dados_iniciais = [
            {"Categoria": "Pizzaria", "Empresa": "Pizzaria do João", "Votos": 10},
            {"Categoria": "Pizzaria", "Empresa": "Pizza Express", "Votos": 8},
            {"Categoria": "Academia", "Empresa": "Fit Life", "Votos": 15},
            {"Categoria": "Academia", "Empresa": "Musclestrog", "Votos": 12},
        ]
        df = pd.concat([df, pd.DataFrame(dados_iniciais)], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        return df
    return pd.read_csv(DATA_FILE)

# Função para salvar voto
def salvar_voto(categoria, empresa):
    df = carregar_dados()
    
    # Verifica se a empresa já existe naquela categoria
    filtro = (df["Categoria"] == categoria) & (df["Empresa"] == empresa)
    
    if filtro.any():
        # Adiciona voto a existente
        df.loc[filtro, "Votos"] += 1
    else:
        # Cria nova empresa com 1 voto
        novo_registro = pd.DataFrame([{"Categoria": categoria, "Empresa": empresa, "Votos": 1}])
        df = pd.concat([df, novo_registro], ignore_index=True)
    
    df.to_csv(DATA_FILE, index=False)
    return df

# --- INTERFACE ESTILO CHAT ---

st.title("🏆 Melhores do Ano")
st.markdown("---")

# Inicializa o estado da sessão (Memória do Chat)
if "passo" not in st.session_state:
    st.session_state.passo = 1
if "categoria_escolhida" not in st.session_state:
    st.session_state.categoria_escolhida = ""

df = carregar_dados()

# PASSO 1: Escolher Categoria
if st.session_state.passo == 1:
    with st.chat_message("assistant"):
        st.write("Olá! Bem-vindo à votação oficial da cidade.")
        st.write("Para começar, escolha uma categoria para votar:")
    
    categorias_unicas = df["Categoria"].unique()
    
    # Exibe botões para as categorias
    col1, col2 = st.columns(2)
    for i, cat in enumerate(categorias_unicas):
        col = col1 if i % 2 == 0 else col2
        if col.button(cat, use_container_width=True):
            st.session_state.categoria_escolhida = cat
            st.session_state.passo = 2
            st.rerun()

# PASSO 2: Escolher Empresa ou Adicionar Nova
elif st.session_state.passo == 2:
    cat = st.session_state.categoria_escolhida
    
    # Histórico da conversa
    with st.chat_message("user"):
        st.write(f"Quero votar em: {cat}")
    
    with st.chat_message("assistant"):
        st.write(f"Ótimo! Quem é o melhor em **{cat}**?")
        st.write("Selecione abaixo ou digite um novo nome se não encontrar.")

    # Filtra empresas da categoria
    empresas_da_cat = df[df["Categoria"] == cat]
    lista_empresas = empresas_da_cat["Empresa"].tolist()
    
    # Formulário de votação
    with st.form("form_voto"):
        # Opção de escolher da lista ou digitar novo
        escolha = st.radio("Escolha um candidato:", ["➕ ADICIONAR NOVO"] + lista_empresas)
        
        # Campo para digitar o nome (só aparece se necessário, mas deixamos visível pela simplicidade)
        novo_nome = st.text_input("Se escolheu 'Adicionar Novo', digite o nome da empresa aqui:")
        
        botao_votar = st.form_submit_button("✅ Confirmar Voto")

        if botao_votar:
            empresa_final = ""
            
            if escolha == "➕ ADICIONAR NOVO":
                if novo_nome:
                    empresa_final = novo_nome.strip().title() # Formata o texto
                else:
                    st.warning("Por favor, digite o nome da nova empresa.")
            else:
                empresa_final = escolha
            
            if empresa_final:
                salvar_voto(cat, empresa_final)
                st.session_state.empresa_voted = empresa_final
                st.session_state.passo = 3
                st.rerun()

# PASSO 3: Confirmação e Gráfico
elif st.session_state.passo == 3:
    cat = st.session_state.categoria_escolhida
    emp = st.session_state.empresa_voted
    
    # Recarrega dados atualizados
    df_atualizado = carregar_dados()
    
    with st.chat_message("user"):
        st.write(f"Meu voto vai para: {emp}")
        
    with st.chat_message("assistant"):
        st.success(f"Voto confirmado para **{emp}**!")
        st.write("Confira como está a disputa agora:")
    
    # Prepara dados para o gráfico
    dados_grafico = df_atualizado[df_atualizado["Categoria"] == cat].sort_values("Votos", ascending=True)
    
    # Exibe gráfico de barras
    st.bar_chart(dados_grafico, x="Votos", y="Empresa", color="#FF4B4B", horizontal=True)
    
    st.markdown("---")
    if st.button("🔄 Votar em outra categoria"):
        st.session_state.passo = 1
        st.session_state.categoria_escolhida = ""
        st.rerun()
