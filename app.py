import streamlit as st
import os
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from PIL import Image
import io

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do SQLite
DATABASE_URL = 'sqlite:///portfolio.db'
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo do banco de dados
class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, index=True)
    premissa = Column(String, nullable=False)
    competencia = Column(String, nullable=False)
    macro_indicador = Column(String, nullable=False)
    micro_indicador = Column(String, nullable=False)
    acao = Column(Text, nullable=False)
    evidencias = Column(String, nullable=True)  # Armazena os caminhos das imagens separadas por vírgula
    descricao = Column(Text, nullable=False)


# Criar tabelas
Base.metadata.create_all(bind=engine)

# Diretórios para salvar arquivos
if not os.path.exists('posts'):
    os.makedirs('posts')
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# Configurações da página
st.set_page_config(page_title="Portfólio", layout="wide")

# Dados de login (exemplo simples)
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

# Função para login
def login():
    st.title("Login")
    username = st.text_input("Usuário", key='login_user')
    password = st.text_input("Senha", type="password", key='login_pass')
    
    if st.button("Entrar", key='login_button'):
        if username == USERNAME and password == PASSWORD:
            st.session_state['logged_in'] = True
            st.success("Login bem-sucedido!")
            st.session_state['page'] = "Administração de Posts"
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")

# Função para logout
def logout():
    if st.button("Sair", key='logout_button'):
        st.session_state.pop('logged_in', None)
        st.success("Você saiu com sucesso!")
        st.session_state['page'] = "Posts Públicos"
        st.rerun()

# Função para salvar post em arquivo markdown (adaptada)
def save_post_to_file(premissa, competencia, macro_indicador, micro_indicador, acao, evidencias, descricao):
    file_name = f"posts/{premissa.replace(' ', '_')}.md"  # Nome do arquivo baseado na premissa
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(f"# {premissa}\n\n")
        f.write(f"**Competência:** {competencia}\n\n")
        f.write(f"**Macro Indicador:** {macro_indicador}\n\n")
        f.write(f"**Micro Indicador:** {micro_indicador}\n\n")
        f.write(f"**Ação:** {acao}\n\n")
        f.write(f"**Descrição:** {descricao}\n\n")

        if evidencias:
            evidencias_list = evidencias.split(',')  # Divide a string de caminhos
            for evidencie in evidencias_list:
                f.write(f"![Evidencia]({evidencie})\n")
    return file_name


# Página de administração (adaptada)
def admin_page():
    st.title("Administração de Posts")

    if st.session_state.get('logged_in'):
        premissa = st.text_input("Premissa", key='post_premissa')
        competencia = st.text_input("Competência", key='post_competencia')
        macro_indicador = st.text_input("Macro Indicador", key='post_macro_indicador')
        micro_indicador = st.text_input("Micro Indicador", key='post_micro_indicador')
        acao = st.text_area("Ação", key='post_acao')
        descricao = st.text_area("Descrição", key='post_descricao')
        uploaded_files = st.file_uploader("Upload de Evidências (Imagens)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True, key='post_evidencias')

        if st.button("Publicar", key='publish_button'):
            evidencias_paths = []
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    image = Image.open(uploaded_file)
                    # Redimensiona a imagem (exemplo: largura máxima 800px)
                    image.thumbnail((800, 600))  # Ajuste o tamanho conforme necessário
                    
                    file_path = os.path.join('uploads', uploaded_file.name)
                    image.save(file_path) # Salva a imagem redimensionada
                    evidencias_paths.append(file_path)

            evidencias_str = ",".join(evidencias_paths) if evidencias_paths else None # Cria string com caminhos separados por virgula

            # Salvar post como arquivo markdown (adaptado)
            post_file = save_post_to_file(premissa, competencia, macro_indicador, micro_indicador, acao, evidencias_str, descricao)

            # Salvar post no SQLite (adaptado)
            db = SessionLocal()
            new_post = Post(premissa=premissa, competencia=competencia, macro_indicador=macro_indicador, micro_indicador=micro_indicador, acao=acao, evidencias=evidencias_str, descricao=descricao)
            db.add(new_post)
            db.commit()
            db.close()

            st.success("Post publicado com sucesso!")
            st.session_state['page'] = "Posts Públicos"
            st.rerun()

        logout()
    else:
        st.warning("Você precisa estar logado para acessar esta página.")
        login()


# Página pública para visualizar posts (adaptada)
def public_page():
    st.title("Portfólio Desenvolvimento de sistemas")

    db = SessionLocal()
    posts = db.query(Post).all()
    db.close()

    for post in posts:
        st.subheader(post.premissa)
        st.write(f"**Competência:** {post.competencia}")
        st.write(f"**Macro Indicador:** {post.macro_indicador}")
        st.write(f"**Micro Indicador:** {post.micro_indicador}")
        st.write(f"**Ação:** {post.acao}")
        st.write(f"**Descrição:** {post.descricao}")

        if post.evidencias:
            evidencias_list = post.evidencias.split(',')
            for evidencie in evidencias_list:
                if evidencie.endswith(('png', 'jpg', 'jpeg')):
                    st.image(evidencie)
                elif evidencie.endswith('mp4'):
                    st.video(evidencie)
        st.markdown("---")

# Menu de navegação
if 'page' not in st.session_state:
    st.session_state['page'] = "Portfólio"

menu = st.sidebar.selectbox("Menu", ["Portfólio", "Administração de Posts"], index=["Portfólio", "Administração de Posts"].index(st.session_state['page']))

if menu == "Portfólio":
    public_page()
    st.session_state['page'] = "Portfólio"
elif menu == "Administração de Posts":
    admin_page()
    st.session_state['page'] = "Administração de Posts"


