import {readFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const dist = path.resolve(root,process.argv[2] || 'dist');
const model = await readFile(path.join(dist,'assets/taipei101.glb'));
assert.equal(model.readUInt32LE(0),0x46546c67,'GLB magic');
assert.equal(model.readUInt32LE(4),2,'glTF version');
assert.equal(model.readUInt32LE(8),model.length,'GLB byte length');
const gltf = JSON.parse(model.subarray(20,20+model.readUInt32LE(12)).toString());
assert.equal(gltf.scenes.length,1,'Export only the demo scene');
assert(!gltf.nodes.some(n => n.name === 'Cube'),'Default cube leaked');
assert(gltf.meshes.length>30);
assert(!gltf.images?.length,'Model must not include third party imagery');
assert(!gltf.buffers.some(b => b.uri),'GLB buffers must be embedded');
const landmarkIds = ['taipei101','twtc','ticc','trade','hyatt','cityhall'];
for(const id of landmarkIds) assert(gltf.nodes.some(n => n.extras?.landmark === id),`Missing landmark: ${id}`);
assert(gltf.nodes.some(n => n.extras?.night_only && n.extras?.landmark === 'taipei101'),'Missing tower lights');
assert(gltf.nodes.some(n => n.extras?.night_only && n.extras?.landmark === 'streetlights'),'Missing street lights');
assert(gltf.materials.some(m => m.name.startsWith('Night') && m.emissiveFactor.some(v => v>0)),'Missing emissive light surfaces');
for(const a of gltf.accessors) {
  if(a.min) assert(a.min.every(Number.isFinite));
  if(a.max) assert(a.max.every(Number.isFinite));
}
// Blender exports the mesh coordinates in glTF Y-up. Check the actual tower vertices.
const tipNodes = gltf.nodes.filter(n => n.extras?.landmark === 'taipei101' && n.mesh !== undefined);
assert(tipNodes.every(n => !n.matrix && !n.rotation && !n.translation && !n.scale),'Unexpected tower node transform');
const towerTop = Math.max(...tipNodes.flatMap(n => gltf.meshes[n.mesh].primitives.map(p => gltf.accessors[p.attributes.POSITION].max[1])));
assert(Math.abs(towerTop-508)<.02,`Tower tip geometry is ${towerTop}, expected 508 m`);
// Shape regressions from the Hall 1 reference review. Read actual exported
// triangles: a valid GLB or a correct tower height cannot catch an open lawn.
const binStart = 20+model.readUInt32LE(12)+8;
function accessorValues(index) {
  const a=gltf.accessors[index], view=gltf.bufferViews[a.bufferView];
  const components={SCALAR:1,VEC3:3}[a.type];
  const sizes={5121:1,5123:2,5125:4,5126:4};
  const bytes=sizes[a.componentType];
  assert(components && bytes,'Unsupported review accessor');
  const stride=view.byteStride || components*bytes;
  const start=binStart+(view.byteOffset || 0)+(a.byteOffset || 0);
  const read={5121:'readUInt8',5123:'readUInt16LE',5125:'readUInt32LE',5126:'readFloatLE'}[a.componentType];
  return Array.from({length:a.count},(_,i) => Array.from({length:components},(_,j) => model[read](start+i*stride+j*bytes)));
}
const hallTriangles=[];
for(const n of gltf.nodes.filter(n => n.extras?.landmark==='twtc' && n.extras.layer==='Surroundings' && n.mesh!==undefined)) {
  assert(!n.matrix && !n.translation && !n.rotation && !n.scale,'Unexpected Hall 1 transform');
  for(const p of gltf.meshes[n.mesh].primitives) {
    assert(p.mode===undefined || p.mode===4,'Expected triangles');
    const vertices=accessorValues(p.attributes.POSITION), indices=accessorValues(p.indices).flat();
    for(let i=0;i<indices.length;i+=3) hallTriangles.push(indices.slice(i,i+3).map(j => vertices[j]));
  }
}
function roofHeight(x,north) {
  const z=-north; let top=-Infinity;
  for(const [a,b,c] of hallTriangles) {
    const det=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2]);
    if(Math.abs(det)<1e-8) continue;
    const u=((b[2]-c[2])*(x-c[0])+(c[0]-b[0])*(z-c[2]))/det;
    const v=((c[2]-a[2])*(x-c[0])+(a[0]-c[0])*(z-c[2]))/det;
    if(u>=-1e-6 && v>=-1e-6 && u+v<=1+1e-6) top=Math.max(top,u*a[1]+v*b[1]+(1-u-v)*c[1]);
  }
  return top;
}
const hallCoverage=[];
for(const dx of [-26,0,26]) for(const dy of [-25,0,25]) {
  const height=roofHeight(-275+dx,10+dy);
  assert(height>25,`Hall 1 centre is open at ${dx},${dy}: top ${height}`);
  hallCoverage.push({east:-275+dx,north:10+dy,height});
}
const vaultProfile=[-313,-275,-237].map(x => roofHeight(x,10));
assert(vaultProfile[1]>Math.max(vaultProfile[0],vaultProfile[2])+2,'Hall 1 central roof must be curved');
const terraces={west:[-374,-359,-344].map(x => roofHeight(x,10)),east:[-176,-191,-206].map(x => roofHeight(x,10))};
for(const [side,heights] of Object.entries(terraces)) {
  assert(heights.every(Number.isFinite),`Missing ${side} terrace`);
  assert(heights[1]>heights[0]+3 && heights[2]>heights[1]+3,`Hall 1 ${side} wings must step up toward the centre: ${heights}`);
}
const html = await readFile(path.join(dist,'index.html'),'utf8');
assert(!/\/\*__(?:MODEL|APP|STYLE)__\*\//.test(html),'Unresolved build marker');
const encoded = html.match(/<script id="model-data" type="application\/octet-stream">([^<]+)<\/script>/)?.[1];
assert(encoded && Buffer.from(encoded,'base64').equals(model),'Embedded GLB differs from download');
assert(!/<script[^>]+src=/i.test(html),'External runtime script');
assert(!/<link[^>]+rel="stylesheet"/i.test(html),'External stylesheet');
assert(!/KMFA|kmfa|美術館/.test(html),'Starter copy leaked');
const info = JSON.parse(await readFile(path.join(dist,'assets/model-info.json'),'utf8'));
assert.equal(info.tower_tip_m,508); assert.equal(info.tier_count,8); assert.equal(info.glb_bytes,model.length);
console.log(JSON.stringify({valid:true,meshes:gltf.meshes.length,materials:gltf.materials.length,
  towerGeometryTipMetres:towerTop,landmarks:landmarkIds,modelBytes:model.length,
  standaloneHtmlBytes:Buffer.byteLength(html),externalRuntimeDependencies:0,
  hall1Geometry:{coveredCentreSamples:hallCoverage,vaultProfile,terraces}},null,2));
