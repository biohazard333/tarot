import os
import openai
import random
from gtts import gTTS 
import streamlit as st
import subprocess
import requests

openai.api_key = "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"

cartas_tarot = [
    "amantes", "carroza", "colgado", "diablo", "emperador",
    "emperatriz", "ermitaño", "estrella", "fortuna",
    "fuerza", "juicio", "justicia", "loco", "luna",
    "mago", "muerte", "mundo", "sacerdote", "sacerdotiza",
    "sol", "templanza", "torre"
]

def seleccionar_cartas_tarot(cantidad):
    return random.sample(cartas_tarot, cantidad)

def generate_audio(text, output_path):
    tts = gTTS(text, lang='es')
    tts.save(output_path)

def generate_video(audio_path, face_image_path, video_path):
    command = f"python3 inference.py --checkpoint_path checkpoints/wav2lip_gan.pth --face face.jpg --audio temp/temp.wav --outfile video.mp4stream --nosmooth"
    process = subprocess.run(command, shell=True, text=True)
    return process.returncode

# Descargar el archivo wav2lip_gan.pth si no existe
checkpoint_path = "checkpoints/wav2lip_gan.pth"
if not os.path.exists(checkpoint_path):
    url = "https://huggingface.co/spaces/salomonsky/tarot/resolve/main/checkpoints/wav2lip_gan.pth"
    response = requests.get(url)

    if response.status_code == 200:
        os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
        with open(checkpoint_path, "wb") as file:
            file.write(response.content)
        print("Archivo descargado exitosamente.")
    else:
        print("Error al descargar el archivo.")

# Crear la carpeta 'temp' si no existe
os.makedirs('temp', exist_ok=True)

def generate_output(name):
    if not name:
        return None, "El campo de nombre es obligatorio."

    cartas_seleccionadas = seleccionar_cartas_tarot(4)
    
    st.image([f"{carta}.png" for carta in cartas_seleccionadas], caption=cartas_seleccionadas, width=100)
    
    prompt = f"Interpretando las cartas sobre la pregunta sobre tu lectura es: {', '.join(cartas_seleccionadas)}."
    
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=180,
        temperature=0.6,
        n=1,
        stop=None,
    )
    gpt3_output = response.choices[0].text.strip()
    
    if len(response.choices) == 0 or 'text' not in response.choices[0]:
        return None, "No se pudo generar el texto."

    return cartas_seleccionadas, gpt3_output

name = st.text_input("Escribe tu Pregunta", value="")

if st.button("Tirar Cartas de Tarot"):
    cartas, gpt_output = generate_output(name)
    if cartas and gpt_output:
        st.success("Cartas tiradas exitosamente.")
        st.write(f"Cartas seleccionadas: {', '.join(cartas)}")
        st.write(f"Interpretación de GPT-3: {gpt_output}")
        st.write("Generando video...")

        # Directorio donde se guardará el video
        video_dir = "videos/"
        os.makedirs(video_dir, exist_ok=True)

        # Rutas de los archivos
        audio_path = "temp/temp.wav"  # Cambiado el nombre del archivo de audio
        video_path = f"{video_dir}video.mp4"
        face_image_path = "face.jpg"
        
        # Aquí es donde generas el audio, por ejemplo:
        generate_audio(gpt_output, audio_path)

        # Luego, genera el video usando el código que proporcionaste
        return_code = generate_video(audio_path, face_image_path, video_path)
        if return_code != 0:
            st.error(f"No se pudo generar el video.")
        elif os.path.isfile(video_path):
            st.video(video_path)
        else:
            st.error("No se pudo generar el video.")
    else:
        st.error("Error al generar las cartas y la interpretación.")
