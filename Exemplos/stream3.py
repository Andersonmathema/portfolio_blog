import streamlit as st
from PIL import Image, ImageFont, ImageDraw
import io
import os

def text_on_image(image, text, font_size, color):
    try:
        img = Image.open(image)
        try:
            font = ImageFont.truetype('arial.ttf', font_size)
        except IOError:
            st.warning("Fonte arial.ttf não encontrada. Usando fonte padrão.")
            font = ImageFont.load_default()
        
        draw = ImageDraw.Draw(img)

        iw, ih = img.size
        # Calculate the size of the text
        bbox = draw.textbbox((0, 0), text, font=font)

        # A largura e altura do texto são calculadas a partir das coordenadas da caixa delimitadora
        fw = bbox[2] - bbox[0]
        fh = bbox[3] - bbox[1]

        # Calcule a posição para centralizar o texto
        x = (iw - fw) / 2
        y = (ih - fh) / 2

        # Desenhe o texto na imagem
        draw.text((x, y), text, fill=color, font=font)

        # Salve a imagem resultante em um objeto BytesIO para evitar problemas de armazenamento
        output_image = io.BytesIO()
        img.save(output_image, format='JPEG')
        output_image.seek(0)

        return output_image
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

image = st.file_uploader('Uma imagem', type=['jpg','jpeg'])
text = st.text_input('Sua marca dágua')
color = st.selectbox(
    'Cor da sua marca', ['black', 'white', 'red', 'green']
)
font_size = st.number_input('Tamanho da fonte', min_value=50)

if image:
    if st.button('Aplicar',type='primary'):
        result = text_on_image(image, text, font_size, color)
        if result:
            st.image(result)            
            st.download_button(
                'Baixe agora mesmo sua foto modificada',
                file_name='Imagem_modificada.jpg',
                data = result,
                mime='image/jpg'
                )
else:
    st.warning('Ainda não temos imagem!')
    