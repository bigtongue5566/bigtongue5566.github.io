import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {UnrealBloomPass} from 'three/addons/postprocessing/UnrealBloomPass.js';
import {OutputPass} from 'three/addons/postprocessing/OutputPass.js';

const $ = id => document.getElementById(id);
const host = $('viewport');
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
const mobile = () => host.clientWidth <= 700;
const original = new Map(), context = [], trees = [], labels = [], occluders = [], nightLights = [];
const clay = new THREE.MeshStandardMaterial({color:0xd9d7c9,roughness:.85});
const views = {
  overview:{position:[1180,1090,1410],target:[-125,160,-80],height:970,label:'信義全景'},
  tower:{position:[760,485,950],target:[0,248,0],height:650,label:'竹節主塔'},
  district:{position:[-275,260,480],target:[-275,38,-10],height:320,label:'世貿一館'},
  top:{position:[-90,1900,-84.9],target:[-90,0,-85],height:1180,label:'街廓俯視'}
};
const labelData = [
  ['01','台北 101',[0,516,0],'taipei101'],
  ['02','世貿一館',[-275,46,-10],'twtc'],
  ['03','國際會議中心',[-465,54,59],'ticc'],
  ['04','國貿大樓',[-441,160,-64],'trade'],
  ['05','君悅飯店',[-267,96,-266],'hyatt'],
  ['06','市政府',[-184,61,-493],'cityhall']
];
let renderer, scene, camera, controls, model, sun, hemi, composer;
let ready = false, transition = null, currentView = 'overview', frameHeight = 970, mood = 'day';
let toastTimer, savedBlob;

function toast(message) {
  $('toast').textContent = message;
  $('toast').classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => $('toast').classList.remove('show'),3200);
}
function rawModel() {
  const data = atob($('model-data').textContent.trim());
  return Uint8Array.from(data,c => c.charCodeAt(0));
}
function downloadBlob(blob,name) {
  const href = URL.createObjectURL(blob), a = document.createElement('a');
  a.href = href; a.download = name; document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(href),30000);
}
function projection() {
  const w = host.clientWidth, h = host.clientHeight, aspect = w/h;
  // The desktop poster leaves a quiet column for the title. Portrait centres the tower.
  const scale = mobile() ? ({overview:1100,district:750,top:2600}[currentView] || frameHeight*.93) : frameHeight;
  const shift = mobile() ? .06 : .12;
  const verticalShift = mobile() ? ({overview:130,district:60,top:330}[currentView] || 0) : 0;
  camera.left = -scale*aspect*(.5+shift);
  camera.right = scale*aspect*(.5-shift);
  camera.top = scale/2+verticalShift; camera.bottom = -scale/2+verticalShift;
  camera.updateProjectionMatrix();
}
function resize() {
  if(!renderer) return;
  renderer.setSize(host.clientWidth,host.clientHeight);
  composer?.setSize(host.clientWidth,host.clientHeight);
  projection();
}
function targetFor(name) {
  if(mobile() && name === 'overview') return new THREE.Vector3(-15,195,-10);
  return new THREE.Vector3(...views[name].target);
}
function setView(name,instant = false) {
  const v = views[name]; currentView = name;
  document.body.dataset.view = name;
  $('viewName').textContent = v.label;
  document.querySelectorAll('button[data-view]').forEach(b => {
    const selected = b.dataset.view === name;
    b.classList.toggle('active',selected); b.setAttribute('aria-pressed',String(selected));
  });
  controls.autoRotate = false; $('orbit').checked = false;
  if(instant || reduced) {
    camera.position.fromArray(v.position); controls.target.copy(targetFor(name));
    camera.zoom = 1; frameHeight = v.height; projection(); controls.update(); transition = null;
  } else {
    transition = {started:performance.now(),from:camera.position.clone(),targetFrom:controls.target.clone(),
      heightFrom:frameHeight,zoomFrom:camera.zoom,to:new THREE.Vector3(...v.position),
      targetTo:targetFor(name),heightTo:v.height};
  }
}
function setMood(name) {
  mood = name; document.body.dataset.mood = name;
  document.querySelectorAll('[data-mood]').forEach(b => {
    if(b.tagName !== 'BUTTON') return;
    const selected = b.dataset.mood === name;
    b.classList.toggle('active',selected); b.setAttribute('aria-pressed',String(selected));
  });
  if(!renderer) return;
  const settings = {
    day:{sky:0xeeece4,sun:0xfff5dc,power:3.2,ambient:2.8,position:[-720,1250,680],exposure:1.12},
    golden:{sky:0xece1cb,sun:0xffbb76,power:4.0,ambient:1.9,position:[-950,450,550],exposure:1.06},
    night:{sky:0x172e36,sun:0x9fbff5,power:1.7,ambient:1.55,position:[-600,1350,-680],exposure:1.2}
  }[name];
  scene.background.set(settings.sky); sun.color.set(settings.sun); sun.intensity = settings.power;
  sun.position.fromArray(settings.position); hemi.intensity = settings.ambient;
  hemi.color.set(name === 'night' ? 0x97b6ce : 0xe6eee6);
  renderer.toneMappingExposure = settings.exposure;
  original.forEach(material => {
    if(material.name.startsWith('Night')) material.emissiveIntensity = name === 'night' ? 28 : 0;
    else if(material.name.includes('Warm window')) material.emissiveIntensity = name === 'night' ? 8 : .12;
    else if(/glaz|glass|curtain/i.test(material.name)) {
      material.emissive.set(0x205357);
      material.emissiveIntensity = name === 'night' ? .06 : 0;
    }
  });
  updateNightLights();
}
function setPanel(open) {
  $('settings').hidden = !open;
  $('panelToggle').setAttribute('aria-expanded',String(open));
}
function restoreLayers() {
  context.forEach(o => o.visible = $('surroundings').checked);
  trees.forEach(o => o.visible = $('vegetation').checked);
  if(model) model.traverse(o => { if(o.isMesh) o.material = $('clay').checked ? clay : original.get(o); });
  updateNightLights();
}
function updateNightLights() {
  for(const o of nightLights) {
    const main = ['taipei101','streetlights'].includes(o.userData.landmark);
    o.visible = mood === 'night' && !$('clay').checked && (main || $('surroundings').checked);
  }
}
function renderScene() {
  if(mood === 'night' && composer) composer.render();
  else renderer.render(scene,camera);
}
function showError(error) {
  console.error(error);
  $('loading').innerHTML = '<strong>無法啟動三維畫面</strong><span>請使用支援 WebGL 的瀏覽器。</span>';
  $('viewName').textContent = '模型載入失敗';
}
function init() {
  renderer = new THREE.WebGLRenderer({antialias:true,alpha:false,preserveDrawingBuffer:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio,1.7));
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  host.append(renderer.domElement);
  scene = new THREE.Scene(); scene.background = new THREE.Color(0xeeece4);
  camera = new THREE.OrthographicCamera(-800,800,500,-500,1,6000);
  controls = new OrbitControls(camera,renderer.domElement);
  controls.enableDamping = true; controls.dampingFactor = .075;
  controls.minZoom = .45; controls.maxZoom = 8; controls.maxPolarAngle = Math.PI*.48;
  controls.autoRotateSpeed = .28; controls.screenSpacePanning = true;
  controls.mouseButtons = {LEFT:THREE.MOUSE.ROTATE,MIDDLE:THREE.MOUSE.ROTATE,RIGHT:THREE.MOUSE.PAN};
  controls.addEventListener('start',() => { transition = null; controls.autoRotate = false; $('orbit').checked = false; });
  hemi = new THREE.HemisphereLight(0xe6eee6,0x667663,2.8); scene.add(hemi);
  sun = new THREE.DirectionalLight(0xfff5dc,3.2); sun.castShadow = true;
  sun.shadow.mapSize.set(2048,2048);
  Object.assign(sun.shadow.camera,{left:-880,right:880,top:880,bottom:-880,near:1,far:3500});
  sun.shadow.normalBias = .6; sun.shadow.bias = -.00006;
  sun.target.position.set(-90,100,-85); scene.add(sun,sun.target);
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(18000,18000),new THREE.ShadowMaterial({opacity:.1}));
  ground.rotation.x = -Math.PI/2; ground.position.y = -8.15; ground.receiveShadow = true; scene.add(ground);
  composer = new EffectComposer(renderer);
  composer.setPixelRatio(Math.min(devicePixelRatio,1.25));
  composer.addPass(new RenderPass(scene,camera));
  composer.addPass(new UnrealBloomPass(new THREE.Vector2(host.clientWidth,host.clientHeight),.42,.2,1.1));
  composer.addPass(new OutputPass());
  setView('overview',true); resize(); setMood('day');
  let wasMobile = mobile();
  window.addEventListener('resize',() => {
    if(wasMobile !== mobile()) { wasMobile = mobile(); setView(currentView,true); }
    resize();
  });
  const bytes = rawModel(); savedBlob = new Blob([bytes],{type:'model/gltf-binary'});
  if(location.protocol === 'file:') $('download').href = URL.createObjectURL(savedBlob);
  new GLTFLoader().parse(bytes.buffer,'',g => {
    model = g.scene;
    model.traverse(o => {
      if(!o.isMesh) return;
      const layer = o.userData.layer;
      o.castShadow = !['Details','Streets','Foundation'].includes(layer); o.receiveShadow = true;
      original.set(o,o.material);
      if(['Architecture','Surroundings'].includes(layer)) occluders.push(o);
      if(layer === 'Surroundings') context.push(o);
      if(layer === 'Lighting') nightLights.push(o);
      if(o.userData.landmark === 'trees') trees.push(o);
    });
    scene.add(model); ready = true; restoreLayers(); setMood(mood);
    for(const [number,title,position,landmark] of labelData) {
      const e = document.createElement('div'); e.className = 'landmark';
      const b = document.createElement('b'); b.textContent = number;
      e.append(b,document.createTextNode(title)); $('landmarks').append(e);
      labels.push({e,position:new THREE.Vector3(...position),landmark});
    }
    $('loading').style.opacity = '0';
    document.body.classList.add('ready'); host.dataset.modelState = 'ready';
    setTimeout(() => $('loading').remove(),650);
    renderer.setAnimationLoop(animate);
  },showError);
  renderer.setAnimationLoop(animate);
}
const projected = new THREE.Vector3(), raycaster = new THREE.Raycaster(), labelOffset = new THREE.Vector3();
let lastOcclusion = -Infinity;
function animate(now) {
  if(transition) {
    const p = Math.min((now-transition.started)/1250,1), t = 1-(1-p)**3;
    camera.position.lerpVectors(transition.from,transition.to,t);
    controls.target.lerpVectors(transition.targetFrom,transition.targetTo,t);
    frameHeight = THREE.MathUtils.lerp(transition.heightFrom,transition.heightTo,t);
    camera.zoom = THREE.MathUtils.lerp(transition.zoomFrom,1,t); projection();
    if(p === 1) transition = null;
  }
  controls.update(); renderScene();
  const width = host.clientWidth, height = host.clientHeight, accepted = [];
  const checkOcclusion = now-lastOcclusion > 220;
  if(checkOcclusion) lastOcclusion = now;
  for(const label of labels) {
    projected.copy(label.position).project(camera);
    if(checkOcclusion) {
      raycaster.setFromCamera(projected,camera);
      const hit = raycaster.intersectObjects(occluders.filter(o => o.visible),false)[0];
      const distance = labelOffset.copy(label.position).sub(raycaster.ray.origin).dot(raycaster.ray.direction);
      label.occluded = Boolean(hit && hit.distance < distance-8);
    }
    const x = (projected.x*.5+.5)*width, y = (-projected.y*.5+.5)*height-13;
    const overlap = accepted.some(point => Math.abs(point.x-x)<(mobile()?90:110) && Math.abs(point.y-y)<28);
    const titleArea = mobile() ? x<240 && y<280 : x<345 && y<height*.69;
    const outside = x<32 || x>width-35 || y<94 || y>height-125 || projected.z>1 || projected.z<-1;
    label.e.hidden = !$('labels').checked || (label.landmark!=='taipei101' && !$('surroundings').checked) || label.occluded || overlap || titleArea || outside;
    if(!label.e.hidden) accepted.push({x,y});
    label.e.style.left = x+'px'; label.e.style.top = y+'px';
  }
  $('compassNeedle').style.transform = `rotate(${-controls.getAzimuthalAngle()*180/Math.PI}deg)`;
}
try { init(); } catch(error) { showError(error); }

document.querySelectorAll('button[data-view]').forEach(b => b.addEventListener('click',() => { if(ready) setView(b.dataset.view); }));
document.querySelectorAll('button[data-mood]').forEach(b => b.addEventListener('click',() => setMood(b.dataset.mood)));
for(const id of ['surroundings','vegetation','clay']) $(id).addEventListener('change',restoreLayers);
$('orbit').addEventListener('change',() => { if(controls) { transition = null; controls.autoRotate = $('orbit').checked; } });
$('panelToggle').addEventListener('click',() => setPanel($('settings').hidden));
$('closeSettings').addEventListener('click',() => setPanel(false));
$('reset').addEventListener('click',() => {
  if(!ready) return;
  for(const id of ['surroundings','vegetation','labels']) $(id).checked = true;
  $('clay').checked = false; restoreLayers(); setMood('day'); setView('overview'); toast('已回到信義全景');
});
$('capture').addEventListener('click',() => {
  if(!ready) return;
  renderScene();
  renderer.domElement.toBlob(blob => { if(blob) { downloadBlob(blob,`Taipei101-${currentView}-${mood}.png`); toast('正在下載目前視角'); } },'image/png');
});
$('offline').addEventListener('click',() => {
  const copy = document.documentElement.cloneNode(true);
  copy.querySelector('#viewport').replaceChildren(); copy.querySelector('#viewport').removeAttribute('data-model-state');
  copy.querySelector('#landmarks').replaceChildren(); copy.querySelector('body').classList.remove('ready');
  copy.querySelector('body').dataset.mood = 'day'; copy.querySelector('#settings').hidden = true;
  copy.querySelector('#panelToggle').setAttribute('aria-expanded','false'); copy.querySelector('#about').removeAttribute('open');
  copy.querySelector('#toast').classList.remove('show');
  copy.querySelector('#download').setAttribute('href','assets/taipei101.glb');
  if(!copy.querySelector('#loading')) {
    const loading = document.createElement('div'); loading.id = 'loading'; loading.setAttribute('role','status');
    loading.innerHTML = '<div class="loader-line"></div><strong>正在展開信義街區</strong><span>載入台北 101 三維模型</span>';
    copy.querySelector('.stage').append(loading);
  } else copy.querySelector('#loading').removeAttribute('style');
  downloadBlob(new Blob(['<!doctype html>\n'+copy.outerHTML],{type:'text/html;charset=utf-8'}),'Taipei101-offline.html');
  toast('正在下載可離線開啟的網頁');
});
$('aboutBtn').addEventListener('click',() => { setPanel(false); $('about').showModal(); });
$('closeAbout').addEventListener('click',() => $('about').close());
$('about').addEventListener('click',e => {
  if(e.target !== $('about')) return;
  const r = $('about').getBoundingClientRect();
  if(e.clientX<r.left || e.clientX>r.right || e.clientY<r.top || e.clientY>r.bottom) $('about').close();
});
host.addEventListener('keydown',e => {
  if(!ready) return;
  if(e.key === 'Home') { setView('overview'); e.preventDefault(); }
  if(['+','=','-'].includes(e.key)) {
    transition = null;
    camera.zoom = THREE.MathUtils.clamp(camera.zoom*(e.key==='-'?1/1.15:1.15),.45,8);
    camera.updateProjectionMatrix(); e.preventDefault();
  }
});
document.addEventListener('keydown',e => { if(e.key === 'Escape') setPanel(false); });
document.addEventListener('visibilitychange',() => { if(renderer) renderer.setAnimationLoop(document.hidden ? null : animate); });
