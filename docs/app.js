const app = document.querySelector('#app');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
let catalog;
let skills;
let demos;
let revealObserver;
const filterState = { search: '', category: '' };
const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const route = (kind, id) => `?${kind}=${encodeURIComponent(id)}`;
const external = (url, title, css = '') => url ? `<a class="${css}" href="${escape(url)}" target="_blank" rel="noopener noreferrer">${escape(title)}</a>` : '';
const timecode = time => `${String(Math.floor(time / 60)).padStart(2, '0')}:${String(Math.floor(time % 60)).padStart(2, '0')}`;
const facts = demo => (demo.facts ?? []).map(escape).join(' &nbsp;/&nbsp; ');
const playable = demo => ['video', 'audio'].includes(demo.type);

function feature(demo, small = false) {
  return `<a class="feature${small ? ' compact' : ''}" href="${route('demo', demo.id)}" data-route>
    <div class="feature-image"><img src="${escape(demo.poster || (demo.type === 'image' ? demo.src : 'assets/hero.svg'))}" alt="${escape(demo.title)}的作品預覽" loading="lazy"><span class="play-badge">${playable(demo) ? '播放作品' : '探索作品'} ↗</span></div>
    <div class="feature-copy"><div><h2>${escape(demo.title)}</h2><p>${escape(demo.subtitle || demo.summary)}</p></div><p class="facts">${facts(demo)}</p></div>
  </a>`;
}

function skillRows(items) {
  return items.map((skill, i) => `<a class="skill-row" href="${route('skill', skill.id)}" data-route>
    <span class="row-number">${String(i + 1).padStart(2, '0')}</span>
    <div class="row-art"><img src="${escape(skill.artwork || 'assets/hero.svg')}" alt="" loading="lazy"></div>
    <div class="row-copy"><p class="meta">${escape(skill.category)} / ${escape(skill.license || 'OPEN SOURCE')}</p><h3>${escape(skill.name)}</h3><div class="slug">${escape(skill.id)}</div><p>${escape(skill.summary)}</p></div><span class="row-arrow" aria-hidden="true">↗</span>
  </a>`).join('');
}

function updateDirectory() {
  const query = filterState.search.trim().toLocaleLowerCase();
  const visible = catalog.skills.filter(skill => (!filterState.category || skill.category === filterState.category) &&
    [skill.name, skill.id, skill.summary, ...(skill.tags ?? [])].join(' ').toLocaleLowerCase().includes(query));
  document.querySelector('#skill-rows').innerHTML = visible.length ? skillRows(visible) : '<p class="empty">沒有符合的 Skill，試試其他關鍵字或分類。</p>';
  document.querySelector('#result-count').textContent = `${visible.length} 個 Skill`;
}

function home() {
  const featured = demos.get(catalog.site.featuredDemoId) || catalog.demos[0];
  const categories = [...new Set(catalog.skills.map(skill => skill.category))];
  app.innerHTML = `<section class="hero" aria-labelledby="page-title">
    <img class="hero-art" src="assets/hero.svg" alt="" fetchpriority="high"><div class="hero-shade"></div>
    <div class="hero-copy"><p class="eyebrow">BY ${escape(catalog.site.owner)} / OPEN SOURCE CREATIVE TOOLS</p><h1 id="page-title">SKILL<br>SHOWCASE<span>.</span></h1><p class="tagline">${escape(catalog.site.description)}</p>${featured ? `<a class="cta" href="${route('demo', featured.id)}" data-route>${playable(featured) ? '播放' : '探索'}精選作品 <span aria-hidden="true">↗</span></a>` : '<a class="cta" href="#skills">探索 Skills ↘</a>'}</div>
    <div class="hero-note"><span>ORIGINAL WORKS · REUSABLE SKILLS</span><span>MADE TO CREATE SOMETHING REAL</span></div>
  </section>
  <div class="shell">
    <section class="section reveal" id="works" aria-label="展示作品"><div class="section-label"><span><span class="number">01 /</span> ${featured ? 'FEATURED WORK' : 'WORKS'}</span><span>${catalog.demos.length} ${catalog.demos.length === 1 ? 'WORK' : 'WORKS'}</span></div>${featured ? feature(featured) : '<p class="empty">作品將陸續加入。</p>'}${catalog.demos.length > 1 ? `<div class="work-list">${catalog.demos.filter(demo => demo.id !== featured.id).map(demo => feature(demo, true)).join('')}</div>` : ''}</section>
    <section class="section directory reveal" id="skills" aria-labelledby="skills-title"><div class="section-label"><span><span class="number">02 /</span> THE SKILLS</span><span>EXPLORE · CREATE · SHARE</span></div><div class="directory-head"><h2 id="skills-title">已公開的 Skills</h2><div class="controls"><label class="visually-hidden" for="search">搜尋 Skill</label><input type="search" id="search" placeholder="搜尋名稱或功能" value="${escape(filterState.search)}"><label class="visually-hidden" for="category">選擇分類</label><select id="category"><option value="">所有分類</option>${categories.map(category => `<option value="${escape(category)}" ${filterState.category === category ? 'selected' : ''}>${escape(category)}</option>`).join('')}</select></div></div><p class="result-count" id="result-count" role="status" aria-live="polite"></p><div id="skill-rows"></div></section>
    <div class="open-note"><span>看見成果，再選擇適合你的 Skill。</span>${external(catalog.site.github, '查看全部開源專案 ↗')}</div>
  </div>`;
  document.querySelector('#search').addEventListener('input', event => {filterState.search = event.target.value; updateDirectory();});
  document.querySelector('#category').addEventListener('change', event => {filterState.category = event.target.value; updateDirectory();});
  updateDirectory();
}

function skillPage(skill) {
  const examples = (skill.demoIds ?? []).map(id => demos.get(id)).filter(Boolean);
  app.innerHTML = `<div class="shell detail"><a class="back" href="./#skills" data-home-anchor="skills">← 所有 Skills</a><div class="skill-intro"><div><p class="eyebrow">${escape(skill.category)} / ${escape(skill.license || 'OPEN SOURCE')}</p><div class="detail-heading"><div><h1 id="page-title">${escape(skill.name)}</h1><p class="subtitle">${escape(skill.id)}</p></div></div><p class="skill-description">${escape(skill.description || skill.summary)}</p><ul class="capabilities">${(skill.capabilities ?? []).map(value => `<li>${escape(value)}</li>`).join('')}</ul>${external(skill.repository, '前往 GitHub · 安裝與原始碼 ↗', 'cta')}<div class="usage"><h2>試試這樣使用</h2><pre class="prompt">${escape(skill.usage || `使用 $${skill.id}`)}</pre><button type="button" id="copy-prompt">複製提示詞 ↗</button><span class="visually-hidden" id="copy-status" role="status"></span></div></div><img class="skill-art" src="${escape(skill.artwork || 'assets/hero.svg')}" alt="" loading="eager"></div><h2 class="work-heading">${examples.length ? '用作品看看它的能力' : '示範作品'}</h2><div class="work-list">${examples.length ? examples.map(demo => feature(demo, true)).join('') : '<p class="empty">這個 Skill 的示範作品準備中。可先到 GitHub 查看說明與範例。</p>'}</div></div>`;
  document.querySelector('#copy-prompt').addEventListener('click', async () => {
    try {await navigator.clipboard.writeText(skill.usage || `使用 $${skill.id}`); document.querySelector('#copy-prompt').textContent = '已複製'; document.querySelector('#copy-status').textContent = '提示詞已複製';}
    catch {document.querySelector('#copy-status').textContent = '無法自動複製，請選取上方提示詞。'; document.querySelector('#copy-prompt').textContent = '請選取上方提示詞';}
  });
}

// New content uses the catalog. New media formats add one renderer here.
const mediaRenderers = {
  video: demo => `<div class="player"><video id="media" controls playsinline preload="metadata" poster="${escape(demo.poster || '')}" aria-label="${escape(demo.title)}"><source src="${escape(demo.src)}" type="video/mp4">${external(demo.src, '下載影片')}</video></div>`,
  audio: demo => `<div class="player audio-player">${demo.poster ? `<img src="${escape(demo.poster)}" alt="${escape(demo.title)}封面">` : ''}<audio id="media" controls preload="metadata" aria-label="${escape(demo.title)}"><source src="${escape(demo.src)}">${external(demo.src, '下載音樂')}</audio></div>`,
  image: demo => `<div class="player"><img src="${escape(demo.src)}" alt="${escape(demo.alt || demo.title)}"></div>`,
  interactive: demo => `<div class="player"><iframe src="${escape(demo.src)}" title="${escape(demo.title)}互動示範" sandbox="allow-scripts allow-same-origin" loading="lazy" referrerpolicy="no-referrer"></iframe></div>`,
  link: demo => `<div class="player link-player">${demo.poster ? `<img src="${escape(demo.poster)}" alt="${escape(demo.title)}作品預覽">` : ''}${external(demo.src, '開啟作品 ↗', 'cta')}</div>`
};

function demoPage(demo) {
  const media = mediaRenderers[demo.type];
  app.innerHTML = `<div class="shell detail"><a class="back" href="./#works" data-home-anchor="works">← 所有作品</a><div class="detail-heading"><div><p class="eyebrow">${escape(demo.type.toUpperCase())} / SKILL SHOWCASE</p><h1 id="page-title">${escape(demo.title)}</h1><p class="subtitle">${escape(demo.subtitle || demo.summary)}</p></div><div class="facts">${facts(demo)}</div></div>${media ? media(demo) : '<p class="empty">此作品格式尚未支援。</p>'}
  <div class="player-controls">${['video','audio'].includes(demo.type) ? '<button class="cta" type="button" id="toggle-play">播放作品 ↗</button>' : external(demo.src, '在新頁面開啟 ↗', 'cta')}<div class="downloads">${external(demo.src, '下載／開啟作品 ↗')}${external(demo.audio, '獨立配樂 ↗')}${external(demo.download, '來源套件 ↗')}${external(demo.source, '製作專案 ↗')}</div></div>
  ${demo.chapters?.length && ['video','audio'].includes(demo.type) ? `<nav class="chapters" aria-label="選擇作品段落">${demo.chapters.map(chapter => `<button type="button" data-seek="${chapter.time}" aria-pressed="false"><span>${timecode(chapter.time)}</span>${escape(chapter.title)}</button>`).join('')}</nav>` : ''}
  <div class="detail-body"><div><h2>${escape(demo.summary)}</h2><p>${escape(demo.description)}</p></div><aside class="contributors"><h2>這件作品用到了</h2>${(demo.contributors ?? []).map(contributor => {const skill = skills.get(contributor.skillId); return skill ? `<a class="contributor" href="${route('skill', skill.id)}" data-route><strong>${escape(skill.name)} ↗</strong><span>${escape(contributor.role)}</span></a>` : '';}).join('')}<p class="credit">${escape(demo.credits || '')}</p><p class="credit">${external(demo.rights, '素材來源與授權 ↗')}</p></aside></div></div>`;
  const player = document.querySelector('#media');
  if (player) {
    const control = document.querySelector('#toggle-play');
    const play = () => player.play().catch(error => {if (error.name !== 'AbortError') control.textContent = '請使用播放器的播放按鈕';});
    control.addEventListener('click', () => {if (player.paused) play(); else player.pause();});
    player.addEventListener('play', () => {control.textContent = '暫停作品';});
    player.addEventListener('pause', () => {control.textContent = '播放作品 ↗';});
    const chapters = [...document.querySelectorAll('[data-seek]')];
    chapters.forEach(button => button.addEventListener('click', () => {player.currentTime = Number(button.dataset.seek); play();}));
    player.addEventListener('timeupdate', () => {let active = -1; chapters.forEach((button, i) => {if (Number(button.dataset.seek) <= player.currentTime) active = i;}); chapters.forEach((button, i) => button.setAttribute('aria-pressed', String(i === active)));});
  }
}

function animate() {
  revealObserver?.disconnect();
  if (reducedMotion.matches || !('IntersectionObserver' in window)) return;
  revealObserver = new IntersectionObserver(entries => entries.forEach(entry => {if (entry.isIntersecting) {entry.target.classList.remove('pending'); revealObserver.unobserve(entry.target);}}), {threshold:.08});
  document.querySelectorAll('.reveal').forEach(element => {element.classList.add('pending'); revealObserver.observe(element);});
}

function render(focus = false) {
  document.querySelector('#media')?.pause();
  const params = new URLSearchParams(location.search);
  const skill = params.get('skill');
  const demo = params.get('demo');
  if (skill && skills.has(skill)) {skillPage(skills.get(skill)); document.title = `${skills.get(skill).name} — ${catalog.site.title}`;}
  else if (demo && demos.has(demo)) {demoPage(demos.get(demo)); document.title = `${demos.get(demo).title} — ${catalog.site.title}`;}
  else if (skill || demo) {app.innerHTML = '<div class="shell error"><h1 id="page-title">找不到這個項目</h1><p>它可能已更名，請從目錄選擇。</p><a href="./" data-route>回到展示站 ↗</a></div>'; document.title = `找不到項目 — ${catalog.site.title}`;}
  else {home(); document.title = `${catalog.site.title} — ${catalog.site.owner}`;}
  app.setAttribute('aria-busy', 'false');
  animate();
  if (focus) {app.focus({preventScroll:true}); window.scrollTo({top:0, behavior:'instant'});}
  if (!skill && !demo && location.hash) {requestAnimationFrame(() => document.getElementById(location.hash.slice(1))?.scrollIntoView());}
}

document.addEventListener('click', event => {
  const link = event.target.closest('a[data-route],a[data-home-anchor]');
  if (!link || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
  if (!catalog) return;
  event.preventDefault();
  history.pushState(null, '', link.href);
  render(true);
});
window.addEventListener('popstate', () => {if (catalog) render(true);});
try {
  const response = await fetch('data/catalog.json');
  if (!response.ok) throw new Error('Catalog request failed');
  catalog = await response.json();
  if (catalog.schemaVersion !== 1 || !Array.isArray(catalog.skills) || !Array.isArray(catalog.demos)) throw new Error('Unsupported catalog');
  skills = new Map(catalog.skills.map(skill => [skill.id, skill]));
  demos = new Map(catalog.demos.map(demo => [demo.id, demo]));
  render();
} catch (error) {
  app.setAttribute('aria-busy','false');
  app.innerHTML = '<div class="shell error"><h1>作品目錄暫時無法載入</h1><p>請重新整理，或直接查看 GitHub 專案。</p><a href="https://github.com/bigtongue5566">前往 GitHub ↗</a></div>';
  console.error('Skill catalog could not be loaded:', error.message);
}
