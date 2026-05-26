const localtunnel = require('localtunnel');
const fs = require('fs');
const path = require('path');

const urlFile = path.join(__dirname, 'scratch', 'tunnel_url.txt');

// Ensure scratch dir exists
const scratchDir = path.dirname(urlFile);
if (!fs.existsSync(scratchDir)) {
  fs.mkdirSync(scratchDir, { recursive: true });
}

(async () => {
  console.log('Iniciando LocalTunnel en puerto 5000...');
  try {
    const tunnel = await localtunnel({ port: 5000 });
    console.log('¡Éxito! URL del túnel:', tunnel.url);
    fs.writeFileSync(urlFile, tunnel.url);
    
    tunnel.on('close', () => {
      console.log('Túnel cerrado.');
    });
  } catch (err) {
    console.error('Error al iniciar LocalTunnel:', err);
    fs.writeFileSync(urlFile, 'ERROR: ' + err.message);
  }
})();
