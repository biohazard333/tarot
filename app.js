const express = require('express');
const openai = require('openai');
const _ = require('lodash');
const { gTTS } = require('gtts');
const { exec } = require('child_process');

const openaiApiKey = process.env.OPENAI_API_KEY;
const openaiClient = new openai.OpenAIAPI({ key: openaiApiKey });

const cartasTarot = [
    "amantes", "carroza", "colgado", "diablo", "emperador",
    "emperatriz", "ermitaño", "estrella", "fortuna",
    "fuerza", "juicio", "justicia", "loco", "luna",
    "mago", "muerte", "mundo", "sacerdote", "sacerdotiza",
    "sol", "templanza", "torre"
];

function seleccionarCartasTarot(cantidad) {
    return _.shuffle(cartasTarot).slice(0, cantidad);
}

function generarAudio(texto, rutaSalida) {
    try {
        const tts = new gTTS(texto, 'es');
        tts.save(rutaSalida, (error) => {
            if (error) {
                console.error('Error al generar el audio:', error);
            }
        });
    } catch (error) {
        console.error('Error al generar el audio:', error);
    }
}

function generarVideo(rutaAudio, rutaImagen, rutaVideo) {
    try {
        const comando = `python3 inference.py --checkpoint_path checkpoints/wav2lip_gan.pth --face ${rutaImagen} --audio ${rutaAudio} --outfile ${rutaVideo} --nosmooth`;

        exec(comando, (error, stdout, stderr) => {
            if (error) {
                console.error('Error al generar el video:', stderr);
            }
        });
    } catch (error) {
        console.error('Error al generar el video:', error);
    }
}

const app = express();
app.use(express.static('public'));
app.use(express.json());

app.post('/tirar-cartas', (req, res) => {
    const nombre = req.body.nombre;

    if (!nombre) {
        return res.status(400).json({ error: 'El campo de nombre es obligatorio.' });
    }

    const cartasSeleccionadas = seleccionarCartasTarot(4);
    const prompt = `Interpretando las cartas sobre la pregunta sobre tu lectura es: ${cartasSeleccionadas.join(', ')}.`;

    openaiClient.createChatCompletion({
        model: 'gpt-3.5-turbo',
        messages: [{ role: 'system', content: 'You are a helpful assistant.' }, { role: 'user', content: prompt }],
    }).then((response) => {
        try {
            const gpt3Output = response.choices[0].message.content.trim();

            const rutaAudio = 'public/temp/temp.wav';
            const rutaVideo = 'public/videos/video.mp4';
            const rutaImagen = 'public/face.jpg';

            generarAudio(gpt3Output, rutaAudio);
            generarVideo(rutaAudio, rutaImagen, rutaVideo);

            res.json({ cartasSeleccionadas, gpt3Output });
        } catch (error) {
            console.error('Error en el manejo de la respuesta de GPT-3:', error);
            res.status(500).json({ error: 'No se pudo generar la interpretación.' });
        }
    }).catch((error) => {
        console.error('Error al obtener la respuesta de GPT-3:', error);
        res.status(500).json({ error: 'No se pudo generar la interpretación.' });
    });
});

const puerto = process.env.PORT || 3000;
app.listen(puerto, () => {
    console.log(`Servidor escuchando en el puerto ${puerto}`);
});
