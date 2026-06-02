const { default: makeWASocket, useMultiFileAuthState, delay, fetchLatestBaileysVersion, DisconnectReason } = require("@whiskeysockets/baileys")
const pino = require("pino")
const express = require("express")
const fs = require('fs')
const QRCode = require('qrcode')
const app = express()
const port = 3000

app.get('/', async (req, res) => {
    const number = req.query.number;
    const sessionDir = './ghost_session';

    let htmlHead = `
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GHOST VIP PANEL</title>
        <style>
            body { background: #000; color: #fff; font-family: sans-serif; text-align: center; padding: 20px; }
            .box { border: 1px solid #333; padding: 30px; border-radius: 15px; background: #0a0a0a; display: inline-block; min-width: 300px; box-shadow: 0 0 20px rgba(255,255,255,0.1); }
            h1 { letter-spacing: 5px; color: #fff; }
            input { width: 80%; padding: 10px; margin: 10px 0; background: #111; border: 1px solid #444; color: #fff; border-radius: 5px; }
            button { padding: 10px 20px; background: #fff; color: #000; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; }
            .p-code { font-size: 2rem; color: #00ffcc; margin: 20px 0; font-weight: bold; border: 2px dashed #333; padding: 10px; }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>GHOST 👻</h1>
    `;

    if (!number) {
        res.send(htmlHead + `
            <p>Enter number with country code</p>
            <form action="/" method="get">
                <input type="text" name="number" placeholder="923024138106" required>
                <br><br>
                <button type="submit">GENERATE VIP LINK</button>
            </form>
        </div></body></html>`);
    } else {
        res.write(htmlHead + `<p id="status">Connecting to WhatsApp Server...</p><div id="result"></div></div>`);
        
        try {
            if (fs.existsSync(sessionDir)) { fs.rmSync(sessionDir, { recursive: true, force: true }); }
            const { state, saveCreds } = await useMultiFileAuthState(sessionDir);
            
            const sock = makeWASocket({
                auth: state,
                printQRInTerminal: false, // Hum browser pe dikhayenge
                logger: pino({ level: "silent" }),
                browser: ["GHOST Bot", "Chrome", "20.0.0"]
            });

            sock.ev.on('creds.update', saveCreds);

            // Pairing Code Request
            setTimeout(async () => {
                try {
                    let code = await sock.requestPairingCode(number.trim());
                    res.write(`<script>
                        document.getElementById('status').innerText = 'Pairing Code Generated!';
                        document.getElementById('result').innerHTML = '<div class="p-code">${code}</div><p>Open WhatsApp > Linked Devices > Link with phone number instead and enter this code.</p>';
                    </script>`);
                    res.end();
                } catch (e) {
                    res.write(`<script>document.getElementById('status').innerText = 'Error: Try again later.';</script>`);
                    res.end();
                }
            }, 5000);

            sock.ev.on('connection.update', (update) => {
                const { connection } = update;
                if (connection === 'open') { console.log('GHOST Bot is Online Now!'); }
            });

        } catch (err) {
            res.write("System Error!");
            res.end();
        }
    }
});

app.listen(port, () => { console.log(`Panel Live: http://localhost:${port}`); });

