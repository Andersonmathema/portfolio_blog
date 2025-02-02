import streamlit as st
import os
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

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
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    file_path = Column(String, nullable=True)

# Criar tabelas
Base.metadata.create_all(bind=engine)

# Diretório para salvar arquivos
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

# Função para salvar post em arquivo markdown
def save_post_to_file(title, content, file_path=None):
    file_name = f"posts/{title.replace(' ', '_')}.md"
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n{content}\n")
        if file_path:
            f.write(f"\n![Media]({file_path})\n")
    return file_name

# Página de administração (apenas para usuários logados)
def admin_page():
    st.title("Administração de Posts")
    
    if st.session_state.get('logged_in'):
        title = st.text_input("Título do Post", key='post_title')
        content = st.text_area("Conteúdo do Post", key='post_content')
        file = st.file_uploader("Upload de Imagem/Vídeo", type=['png', 'jpg', 'jpeg', 'mp4'], key='post_file')

        if st.button("Publicar", key='publish_button'):
            file_path = None
            if file:
                file_path = os.path.join('uploads', file.name)
                with open(file_path, 'wb') as f:
                    f.write(file.read())

            # Salvar post como arquivo markdown
            post_file = save_post_to_file(title, content, file_path)

            # Salvar post no SQLite
            db = SessionLocal()
            new_post = Post(title=title, content=content, file_path=file_path)
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

# Página pública para visualizar posts
def public_page():
    st.title("Posts Públicos")
    
    db = SessionLocal()
    posts = db.query(Post).all()
    db.close()

    for post in posts:
        st.subheader(post.title)
        st.write(post.content)
        if post.file_path:
            if post.file_path.endswith(('png', 'jpg', 'jpeg')):
                st.image(post.file_path)
            elif post.file_path.endswith('mp4'):
                st.video(post.file_path)
        st.markdown("---")

# Menu de navegação
if 'page' not in st.session_state:
    st.session_state['page'] = "Posts Públicos"

menu = st.sidebar.selectbox("Menu", ["Posts Públicos", "Administração de Posts"], index=["Posts Públicos", "Administração de Posts"].index(st.session_state['page']))

if menu == "Posts Públicos":
    public_page()
    st.session_state['page'] = "Posts Públicos"
elif menu == "Administração de Posts":
    admin_page()
    st.session_state['page'] = "Administração de Posts"


