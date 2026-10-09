import http from 'node:http';
import {readFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const base = path.join(root,'dist');
const port = Number(process.env.DEMO_PORT || 4190);
const types = {'.html':'text/html; charset=utf-8','.glb':'model/gltf-binary','.png':'image/png','.json':'application/json'};
http.createServer(async(req,res) => {
  try {
    const rel = decodeURIComponent(new URL(req.url,'http://localhost').pathname);
    const target = path.resolve(base,'.'+(rel === '/' ? '/index.html' : rel));
    if(!target.startsWith(base+path.sep)) { res.writeHead(403); res.end(); return; }
    const bytes = await readFile(target);
    res.writeHead(200,{'Content-Type':types[path.extname(target)] || 'application/octet-stream','Cache-Control':'no-cache'});
    res.end(bytes);
  } catch { res.writeHead(404); res.end('Not found'); }
}).listen(port,'127.0.0.1',() => console.log(`Local: http://127.0.0.1:${port}`));
