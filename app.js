const { exec } = require('child_process');

// Comando para ejecutar el archivo Python
const pythonCommand = 'streamlit run app.py';

// Ejecutar el comando
exec(pythonCommand, (error, stdout, stderr) => {
  if (error) {
    console.error(`Error al ejecutar el comando: ${error}`);
    return;
  }
  console.log(`Salida del comando: ${stdout}`);
});
