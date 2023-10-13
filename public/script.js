document.getElementById('form').addEventListener('submit', function(e) {
    e.preventDefault();
    const nombre = document.getElementById('nombre').value;

    fetch('/tirar-cartas', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ nombre }),
    })
    .then(response => response.json())
    .then(data => {
        const resultadoDiv = document.getElementById('resultado');
        resultadoDiv.innerHTML = `
            <h2>Resultado de la Lectura:</h2>
            <p>Cartas Seleccionadas: ${data.cartasSeleccionadas.join(', ')}</p>
            <p>Interpretación GPT-3: ${data.gpt3Output}</p>
            <audio controls>
                <source src="temp/temp.wav" type="audio/wav">
                Tu navegador no soporta la reproducción de audio.
            </audio>
            <video controls>
                <source src="videos/video.mp4" type="video/mp4">
                Tu navegador no soporta la reproducción de video.
            </video>
        `;
    })
    .catch(error => console.error('Error:', error));
});
