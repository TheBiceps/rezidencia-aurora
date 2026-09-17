#!/usr/bin/env node
/* ---------------------------------------------------------------------------
 * P6 — one PDF per apartment
 *
 *   python3 rezidencia/_build/build_pages.py     (writes _build/pdf/karta.html)
 *   node rezidencia/_build/pdf/build_pdfs.mjs    (writes assets/pdf/P6-byt-*.pdf)
 *
 * Opens the print template in headless Chrome once per apartment and prints it
 * to A4. The PDFs are static files, so they are a snapshot: RE-RUN THIS whenever
 * data.js changes (areas, status, price) or the contact details are replaced.
 * Each PDF footer carries the date it was made.
 *
 * ONLY=1.B,3.H limits a run to those apartments (and leaves other PDFs alone).
 *
 * Needs Google Chrome (override the path with CHROME=...) and network access for
 * the Inter webfont. Node 22+ (built-in WebSocket).
 * ------------------------------------------------------------------------ */

import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { setTimeout as sleep } from 'node:timers/promises';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const OUT = path.join(ROOT, 'assets', 'pdf');
const CHROME = process.env.CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

/* detail.js builds the same name for its download button */
const pdfName = id => `P6-byt-${id.replace('.', '')}.pdf`;

const TYPES = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript',
  '.webp': 'image/webp', '.jpg': 'image/jpeg', '.png': 'image/png', '.svg': 'image/svg+xml',
  '.woff2': 'font/woff2', '.json': 'application/json',
};

function serve() {
  const server = http.createServer((req, res) => {
    const file = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
    if (!file.startsWith(ROOT)) { res.writeHead(403); return res.end(); }
    fs.readFile(file, (err, body) => {
      if (err) { res.writeHead(404); return res.end(); }
      res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream' });
      res.end(body);
    });
  });
  return new Promise(resolve => server.listen(0, '127.0.0.1', () => resolve(server)));
}

async function launch() {
  const dir = fs.mkdtempSync(path.join(fs.realpathSync(process.env.TMPDIR || '/tmp'), 'p6pdf-'));
  const proc = spawn(CHROME, ['--headless=new', '--remote-debugging-port=0', `--user-data-dir=${dir}`,
    '--no-first-run', '--no-default-browser-check', 'about:blank'], { stdio: ['ignore', 'ignore', 'pipe'] });
  const wsUrl = await new Promise((resolve, reject) => {
    let buf = '';
    proc.stderr.on('data', d => {
      buf += d;
      const m = buf.match(/DevTools listening on (ws:\/\/\S+)/);
      if (m) resolve(m[1]);
    });
    proc.on('exit', code => reject(new Error(`Chrome exited (${code})`)));
    setTimeout(() => reject(new Error('Chrome did not start')), 20000);
  });
  const port = new URL(wsUrl).port;
  const targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  const ws = new WebSocket(targets.find(t => t.type === 'page').webSocketDebuggerUrl);
  await new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = reject; });
  let seq = 0;
  const pending = new Map();
  ws.onmessage = e => {
    const m = JSON.parse(e.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
  };
  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const id = ++seq;
    pending.set(id, m => (m.error ? reject(new Error(`${method}: ${m.error.message}`)) : resolve(m.result)));
    ws.send(JSON.stringify({ id, method, params }));
  });
  const close = async () => {
    ws.close();
    const gone = new Promise(resolve => proc.once('exit', resolve));
    proc.kill();
    await Promise.race([gone, sleep(3000)]);
    try { fs.rmSync(dir, { recursive: true, force: true }); } catch { /* Chrome still flushing its profile */ }
  };
  return { send, close };
}

async function main() {
  fs.mkdirSync(OUT, { recursive: true });
  const server = await serve();
  const base = `http://127.0.0.1:${server.address().port}/_build/pdf/karta.html`;
  const chrome = await launch();
  const { send } = chrome;
  const evaluate = async expression =>
    (await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true })).result.value;

  try {
    await send('Page.enable');
    await send('Page.navigate', { url: base });
    await sleep(800);
    const only = process.env.ONLY ? process.env.ONLY.split(',') : null;
    const ids = (await evaluate('APARTMENTS.map(a => a.id)')).filter(id => !only || only.includes(id));
    if (!ids || !ids.length) throw new Error('no apartments read from data.js');

    const made = new Set();
    for (const id of ids) {
      await send('Page.navigate', { url: `${base}?id=${encodeURIComponent(id)}` });
      let state;
      for (let t = 0; t < 150; t++) {
        await sleep(100);
        state = await evaluate('window.__kartaReady').catch(() => undefined);
        if (state) break;
      }
      if (state !== true) throw new Error(`${id}: template not ready (${state})`);
      const { data } = await send('Page.printToPDF', {
        printBackground: true, preferCSSPageSize: true, generateTaggedPDF: true,
        marginTop: 0, marginBottom: 0, marginLeft: 0, marginRight: 0,
      });
      const file = path.join(OUT, pdfName(id));
      fs.writeFileSync(file, Buffer.from(data, 'base64'));
      made.add(path.basename(file));
      console.log(`${pdfName(id).padEnd(16)} ${Math.round(fs.statSync(file).size / 1024)} KB`);
    }

    /* an apartment removed from data.js must not leave its old PDF behind */
    if (!only) for (const f of fs.readdirSync(OUT)) {
      if (f.endsWith('.pdf') && !made.has(f)) { fs.rmSync(path.join(OUT, f)); console.log(`removed ${f}`); }
    }
    console.log(`${made.size} PDFs in ${path.relative(process.cwd(), OUT)}`);
  } finally {
    await chrome.close();
    server.close();
  }
}

main().catch(err => { console.error(err.message); process.exit(1); });
