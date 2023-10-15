const fs = require('fs');
const { execSync } = require('child_process');
const openai = require('openai');
let random;
import('random').then(module => {
    random = module;
});
const gtts = require('gtts');
const request = require('request');
const express = require('express');
const bodyParser = require('body-parser');
const sharp = require('sharp');

const app = express();

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
openai.api_key = OPENAI_API_KEY;

const cartas_tarot = ["amantes", "carroza", "colgado", "diablo", "emperador",
                      "emperatriz", "ermitaño", "estrella", "fortuna",
                      "fuerza", "juicio", "justicia", "loco", "luna",
                      "mago", "muerte", "mundo", "sacerdote", "sacerdotiza",
                      "sol", "templanza", "torre"];

const current_dir = process.cwd();
const static_images_path = `${current_dir}/static/images`;

function seleccionar_cartas_tarot(cantidad) {
    return random.sample(cartas_tarot, cantidad);
}

function generate_audio(text, output_path) {
    const tts = new gtts(text, 'es');
    tts.save(output_path);
}

function generate_video(audio_path, face_image_path, video_path) {
    const command = `python3 inference.py --checkpoint_path checkpoints/wav2lip_gan.pth --face face.jpg --audio ${audio_path} --outfile ${video_path} --nosmooth`;
    execSync(command);
}

const checkpoint_path = "checkpoints/wav2lip_gan.pth";
if (!fs.existsSync(checkpoint_path)) {
    const url = "https://huggingface.co/spaces/salomonsky/tarot/resolve/main/checkpoints/wav2lip_gan.pth";
    request.get(url).pipe(fs.createWriteStream(checkpoint_path));
}

app.get('/', (req, res) => {
    res.sendFile('index.html', { root: __dirname });
});

app.post('/resultado', (req, res) => {
    const name = req.body.pregunta;

    const cartas = seleccionar_cartas_tarot(4);

    const images = cartas.map(carta => {
        const cartaPath = `${static_images_path}/${carta}.png`;
        return sharp(cartaPath).toFile(`temp/${carta}.png`);
    });

    const prompt = `Interpretando las cartas sobre la pregunta sobre tu lectura es: ${cartas.join(', ')}.`;
    openai.Completion.create({
        engine: "text-davinci-003",
        prompt: prompt,
        max_tokens: 180,
        temperature: 0.6,
        n: 1,
        stop: null,
    }).then(response => {
        if (response.choices.length > 0 && 'text' in response.choices[0]) {
            const gpt3_output = response.choices[0].text.trim();

            const audio_path = `temp/temp.wav`;
            const video_dir = `videos/`;
            fs.mkdirSync(video_dir, { recursive: true });
            const video_path = `${video_dir}video.mp4`;
            const face_image_path = `face.jpg`;

            generate_audio(gpt3_output, audio_path);
            generate_video(audio_path, face_image_path, video_path);

            Promise.all(images).then(() => {
                res.send(`
                    Salida de 4 cartas aleatorias: ${cartas.join(', ')}
                    <br>
                    <img src="temp/${cartas[0]}.png" alt="${cartas[0]}">
                    <img src="temp/${cartas[1]}.png" alt="${cartas[1]}">
                    <img src="temp/${cartas[2]}.png" alt="${cartas[2]}">
                    <img src="temp/${cartas[3]}.png" alt="${cartas[3]}">
                    <br>
                    Interpretación del GPT-3: ${gpt3_output}
                    <br>
                    <video width="320" height="240" controls>
                        <source src="${video_path}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                `);
            });
        }
    });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Servidor escuchando en el puerto ${PORT}`);
});
