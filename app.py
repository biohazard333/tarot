import os
import openai
import random
from gtts import gTTS 
import subprocess
import requests
import streamlit as st

# Configuración de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Lista de cartas de tarot
cartas_tarot = ["amantes", "carroza", "colgado", "diablo", "emperador",
                "emperatriz", "ermitaño", "estrella", "fortuna",
                "fuerza", "juicio", "justicia", "loco", "luna",
                "mago", "muerte", "mundo", "sacerdote", "sacerdotiza",
                "sol", "templanza", "torre"]

# Ruta para las imágenes
current_dir = os.getcwd()
static_images_path = os.path.join(current_dir, "static/images")

# Función para seleccionar cartas de tarot al azar
def seleccionar_cartas_tarot(cantidad):
    return random.sample(cartas_tarot, cantidad)

# Función para generar audio a partir de texto
def generate_audio(text, output_path):
    tts = gTTS(text, lang='es')
    tts.save(output_path)

# Función para generar video con Wav2Lip
def generate_video(audio_path, face_image_path, video_path):
    command = f"python3 inference.py --checkpoint_path checkpoints/wav2lip_gan.pth --face face.jpg --audio {audio_path} --outfile {video_path} --nosmooth"
    process = subprocess.run(command, shell=True, text=True)
    return process.returncode

# Comprobación y descarga del archivo de checkpoint si no existe
checkpoint_path = "checkpoints/wav2lip_gan.pth"
if not os.path.exists(checkpoint_path):
    url = "https://huggingface.co/spaces/salomonsky/tarot/resolve/main/checkpoints/wav2lip_gan.pth"
    response = requests.get(url)

    if response.status_code == 200:
        os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
        with open(checkpoint_path, "wb") as file:
            file.write(response.content)

# Configuración de la página Streamlit
st.title("Tirada de Tarot")

# Sección de pregunta
name = st.text_input("1. Haz tu pregunta:")

# Sección de salida de cartas
if name:
    cartas = seleccionar_cartas_tarot(4)
    st.write(f"2. Salida de 4 cartas aleatorias: {', '.join(cartas)}")

    # Mostrar imágenes de las cartas
    st.subheader("Imágenes de las cartas:")
    col1, col2, col3, col4 = st.columns(4)  # Definir 4 columnas

    for i, carta in enumerate(cartas):
        image_path = os.path.join(static_images_path, f"{carta}.png")
        col = [col1, col2, col3, col4][i]  # Seleccionar la columna correspondiente
        col.image(image_path, caption=carta, use_column_width=True, width=100)

    # Sección de interpretación de GPT-3
    prompt = f"Interpretando las cartas sobre la pregunta sobre tu lectura es: {', '.join(cartas)}."
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=180,
        temperature=0.6,
        n=1,
        stop=None,
    )
    
    if len(response.choices) > 0 and 'text' in response.choices[0]:
        gpt3_output = response.choices[0].text.strip()
        st.write(f"3. Interpretación del GPT-3: {gpt3_output}")

        # Sección de video generado por Wav2Lip
        audio_path = "temp/temp.wav"
        video_dir = "videos/"
        os.makedirs(video_dir, exist_ok=True)
        video_path = f"{video_dir}video.mp4"
        face_image_path = "face.jpg"

        generate_audio(gpt3_output, audio_path)
        return_code = generate_video(audio_path, face_image_path, video_path)

        if return_code == 0 and os.path.isfile(video_path):
            st.video(video_path, format="video/mp4")
