const net = require('net'); // eslint-disable-line
const port = process.env.PORT ? process.env.PORT - 100 : 3000;

process.env.ELECTRON_START_URL = `http://localhost:${port}`;

const client = new net.Socket();

let startedElectron = false;
const tryConnection = () =>
  client.connect({ port: port }, () => {
    client.end();
    if (!startedElectron) {
      startedElectron = true;
      const exec = require('child_process').exec;
      exec('npm run electron');
    }
  });

tryConnection();

client.on('error', () => {
  setTimeout(tryConnection, 1000);
});
