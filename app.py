from flask import Flask, render_template, request
import os
import openai
import random
from gtts import gTTS 
import subprocess
import requests

app = Flask(__name__)

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
    command = f"python3 inference.py --checkpoint_path checkpoints/wav2lip_gan.pth --face face.jpg --audio {audio_path} --outfile {video_path} --nosmooth"
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

from flask import Flask, render_template, request
import os
import openai
import random
from gtts import gTTS 
import subprocess
import requests

app = Flask(__name__)

# Resto de tu código...

def generate_output(name):
    if not name:
        return None, "El campo de nombre es obligatorio."

    cartas_seleccionadas = seleccionar_cartas_tarot(4)

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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['pregunta']
        cartas, gpt_output = generate_output(name)
        if cartas and gpt_output:
            audio_path = "temp/temp.wav"
            video_dir = "videos/"
            os.makedirs(video_dir, exist_ok=True)
            video_path = f"{video_dir}video.mp4"
            face_image_path = "face.jpg"

            generate_audio(gpt_output, audio_path)
            return_code = generate_video(audio_path, face_image_path, video_path)
            if return_code == 0 and os.path.isfile(video_path):
                return redirect('https://biohazard333.github.io/tarot', cartas=cartas, gpt_output=gpt_output, video_path=video_path)
            else:
                return "No se pudo generar el video."
        else:
            return "Error al generar las cartas y la interpretación."
    return redirect('https://biohazard333.github.io/tarot')

if __name__ == '__main__':
    app.run(debug=True)
