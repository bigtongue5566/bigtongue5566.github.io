import {build} from 'esbuild';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const dist = path.join(root,'dist');
await mkdir(dist,{recursive:true});
const bundled = await build({absWorkingDir:root,entryPoints:['./src/app.js'],bundle:true,minify:true,
  format:'iife',target:'es2022',write:false,legalComments:'inline'});
const [template,style,model,threeLicence] = await Promise.all([
  readFile(path.join(root,'src/index.html'),'utf8'),
  readFile(path.join(root,'src/style.css'),'utf8'),
  readFile(path.join(dist,'assets/taipei101.glb')),
  readFile(path.join(root,'node_modules/three/LICENSE'),'utf8')
]);
const html = template.replace('</head>',() => `<!-- Bundled Three.js licence:\n${threeLicence}\n-->\n</head>`)
  .replace('/*__STYLE__*/',() => style)
  .replace('/*__MODEL__*/',() => model.toString('base64'))
  .replace('/*__APP__*/',() => bundled.outputFiles[0].text.replace(/<\/script/gi,'<\\/script'))
  .replace(/[ \t]+$/gm,'');
await writeFile(path.join(dist,'index.html'),html);
await writeFile(path.join(dist,'assets/THIRD_PARTY_NOTICES.txt'),threeLicence);
console.log(`Built standalone HTML: ${(Buffer.byteLength(html)/1048576).toFixed(2)} MiB`);
