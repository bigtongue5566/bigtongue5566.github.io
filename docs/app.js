const app = document.querySelector('#app');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
let catalog;
let skills;
let demos;
let revealObserver;
let renderedRoute;
const filterState = { search: '', category: '' };
const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const route = (kind, id) => `?${kind}=${encodeURIComponent(id)}`;
const worksRoute = '?view=works';
const external = (url, title, css = '') => url ? `<a class="${css}" href="${escape(url)}" target="_blank" rel="noopener noreferrer">${escape(title)}</a>` : '';
const timecode = time => `${String(Math.floor(time / 60)).padStart(2, '0')}:${String(Math.floor(time % 60)).padStart(2, '0')}`;
const facts = demo => (demo.facts ?? []).map(escape).join(' &nbsp;/&nbsp; ');
const playable = demo => ['video', 'audio'].includes(demo.type);
const mediaLabels = {video:'影片 Demo',audio:'音樂 Demo',image:'圖片 Demo',interactive:'互動 Demo',link:'作品 Demo'};

function showLocation(kind, item) {
  const section = ['demo','works'].includes(kind) ? 'works' : 'skills';
  document.querySelectorAll('[data-nav]').forEach(link => {if (link.dataset.nav === section) link.setAttribute('aria-current','page'); else link.removeAttribute('aria-current');});
  const breadcrumbs = document.querySelector('#breadcrumbs');
  breadcrumbs.hidden = kind === 'home';
  if (breadcrumbs.hidden) return;
  const current = kind === 'skill' ? item.name : kind === 'demo' ? item.title : kind === 'error' ? '找不到項目' : '作品集';
  const type = kind === 'skill' ? 'Skill 介紹' : kind === 'demo' ? mediaLabels[item.type] || 'Demo' : kind === 'error' ? '頁面未找到' : 'Demo 目錄';
  breadcrumbs.innerHTML = `<ol><li><a href="./" data-route>首頁</a></li>${kind === 'demo' ? `<li><a href="${worksRoute}" data-route>作品集</a></li>` : ''}<li aria-current="page" title="${escape(current)}">${escape(current)}</li></ol><span class="page-type">${escape(type)}</span>`;
}

function feature(demo, small = false) {
  return `<a class="feature${small ? ' compact' : ''}" href="${route('demo', demo.id)}" data-route>
    <div class="feature-image"><img src="${escape(demo.poster || (demo.type === 'image' ? demo.src : 'assets/hero.svg'))}" alt="${escape(demo.title)}的作品預覽" loading="lazy"><span class="play-badge">${escape(mediaLabels[demo.type] || 'Demo')} · ${playable(demo) ? '播放' : '探索'} ↗</span></div>
    <div class="feature-copy"><div><h2>${escape(demo.title)}</h2><p>${escape(demo.subtitle || demo.summary)}</p></div><p class="facts">${facts(demo)}</p></div>
  </a>`;
}

function skillRows(items) {
  return items.map((skill, i) => `<a class="skill-row" href="${route('skill', skill.id)}" data-route>
    <span class="row-number">${String(i + 1).padStart(2, '0')}</span>
    <div class="row-art"><img src="${escape(skill.artwork || 'assets/hero.svg')}" alt="" loading="lazy"></div>
    <div class="row-copy"><p class="meta">${escape(skill.category)} / ${escape(skill.license || 'OPEN SOURCE')}</p><h3>${escape(skill.name)}</h3><div class="slug">${escape(skill.id)}</div><p>${escape(skill.summary)}</p><span class="row-link">查看 Skill</span></div><span class="row-arrow" aria-hidden="true">↗</span>
  </a>`).join('');
}

function groupedWorks(items) {
  const groups = new Map();
  items.forEach(demo => {if (!groups.has(demo.type)) groups.set(demo.type,[]); groups.get(demo.type).push(demo);});
  return [...groups].map(([kind,entries]) => `<div class="work-group"><h3>${escape(mediaLabels[kind] || 'Demo')} <span>${entries.length} 件作品</span></h3><div class="work-list">${entries.map(demo => feature(demo,true)).join('')}</div></div>`).join('');
}

function updateDirectory() {
  const query = filterState.search.trim().toLocaleLowerCase();
  const visible = catalog.skills.filter(skill => (!filterState.category || skill.category === filterState.category) &&
    [skill.name, skill.id, skill.summary, ...(skill.tags ?? [])].join(' ').toLocaleLowerCase().includes(query));
  document.querySelector('#skill-rows').innerHTML = visible.length ? skillRows(visible) : '<p class="empty">沒有符合的 Skill，試試其他關鍵字或分類。</p>';
  document.querySelector('#result-count').textContent = `${visible.length} 個 Skill`;
}

function home() {
  const categories = [...new Set(catalog.skills.map(skill => skill.category))];
  app.innerHTML = `<div class="shell directory-home"><section id="skills" aria-labelledby="page-title">
    <div class="entry-intro"><p class="eyebrow">BY ${escape(catalog.site.owner)} / OPEN SOURCE SKILLS</p><h1 id="page-title">我的 Skills<span>.</span></h1><p>${escape(catalog.site.description)}</p></div>
    <div class="directory-head"><h2>Skills 目錄</h2><div class="controls"><label class="visually-hidden" for="search">搜尋 Skill</label><input type="search" id="search" placeholder="搜尋名稱或功能" value="${escape(filterState.search)}"><label class="visually-hidden" for="category">選擇分類</label><select id="category"><option value="">所有分類</option>${categories.map(category => `<option value="${escape(category)}" ${filterState.category === category ? 'selected' : ''}>${escape(category)}</option>`).join('')}</select></div></div><p class="result-count" id="result-count" role="status" aria-live="polite"></p><div id="skill-rows"></div>
    </section><div class="open-note"><span>選擇 Skill，了解它能完成什麼。</span>${external(catalog.site.github, '查看全部開源專案 ↗')}</div></div>`;
  document.querySelector('#search').addEventListener('input', event => {filterState.search = event.target.value; updateDirectory();});
  document.querySelector('#category').addEventListener('change', event => {filterState.category = event.target.value; updateDirectory();});
  updateDirectory();
}

function worksPage() {
  const featured = demos.get(catalog.site.featuredDemoId) || catalog.demos[0];
  app.innerHTML = `<div class="shell detail gallery"><a class="back" href="./" data-route>← Skills 目錄</a><div class="detail-heading"><div><p class="eyebrow">MADE WITH SKILLS / ORIGINAL WORKS</p><h1 id="page-title">作品集</h1><p class="subtitle">用成品看看 Skills 的能力，選擇作品播放完整 Demo。</p></div><div class="facts">${catalog.demos.length} 件作品</div></div>
    ${featured ? `<div class="section-label"><span>精選作品</span><span>${escape(mediaLabels[featured.type] || 'Demo')}</span></div>${feature(featured)}` : '<p class="empty">作品將陸續加入。</p>'}${groupedWorks(catalog.demos.filter(demo => demo.id !== featured?.id))}</div>`;
}

function skillPage(skill) {
  const examples = (skill.demoIds ?? []).map(id => demos.get(id)).filter(Boolean);
  app.innerHTML = `<div class="shell detail"><a class="back" href="./" data-route>← Skills 目錄</a><div class="skill-intro"><div><p class="eyebrow">${escape(skill.category)} / ${escape(skill.license || 'OPEN SOURCE')}</p><div class="detail-heading"><div><h1 id="page-title">${escape(skill.name)}</h1><p class="subtitle">${escape(skill.id)}</p></div></div><p class="skill-description">${escape(skill.description || skill.summary)}</p><ul class="capabilities">${(skill.capabilities ?? []).map(value => `<li>${escape(value)}</li>`).join('')}</ul>${external(skill.repository, '前往 GitHub · 安裝與原始碼 ↗', 'cta')}<div class="usage"><h2>試試這樣使用</h2><pre class="prompt">${escape(skill.usage || `使用 $${skill.id}`)}</pre><button type="button" id="copy-prompt">複製提示詞 ↗</button><span class="visually-hidden" id="copy-status" role="status"></span></div></div><img class="skill-art" src="${escape(skill.artwork || 'assets/hero.svg')}" alt="" loading="eager"></div><h2 class="work-heading">${examples.length ? '用作品看看它的能力' : '示範作品'}</h2><div class="work-list">${examples.length ? examples.map(demo => feature(demo, true)).join('') : '<p class="empty">這個 Skill 的示範作品準備中。可先到 GitHub 查看說明與範例。</p>'}</div></div>`;
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
  interactive: demo => `<div class="player"><iframe src="${escape(demo.src)}" title="${escape(demo.title)}互動示範" sandbox="allow-scripts allow-same-origin allow-downloads" loading="lazy" referrerpolicy="no-referrer"></iframe></div>`,
  link: demo => `<div class="player link-player">${demo.poster ? `<img src="${escape(demo.poster)}" alt="${escape(demo.title)}作品預覽">` : ''}${external(demo.src, '開啟作品 ↗', 'cta')}</div>`
};

function sourceNotes(demo) {
  if (!demo.references?.length) return '';
  const claims = (demo.claims ?? []).map(claim => `<li><span class="claim-time">${escape(claim.time)}</span><div><p>${escape(claim.text)}</p><div class="claim-links">${claim.sourceIds.map(id => `<a href="#source-${escape(id)}">[${escape(id)}]</a>`).join(' ')}</div></div></li>`).join('');
  const references = demo.references.map(ref => `<li id="source-${escape(ref.id)}"><span class="reference-id">[${escape(ref.id)}]</span><div>${external(ref.url, ref.title + ' ↗')}<p>${escape(ref.scope)}</p><span class="reference-meta">${escape(ref.publisher)} · 查核 ${escape(ref.checkedDate)}${ref.dataYear ? ` · ${escape(ref.dataYear)} 年資料` : ''}</span><div class="reference-url">${escape(ref.url)}</div></div></li>`).join('');
  return `<section class="references" id="references" aria-labelledby="references-title"><h2 id="references-title">資料來源與逐段對照</h2><p class="reference-intro">畫面中的來源編號對應以下官方資料。文字為獨立整理；圖形為概念示意。</p>${claims ? `<ol class="claim-list">${claims}</ol>` : ''}<ol class="reference-list">${references}</ol></section>`;
}

function demoPage(demo) {
  const media = mediaRenderers[demo.type];
  const companion = demos.get(demo.relatedDemoId);
  const companionLink = companion ? `<a href="${route('demo',companion.id)}" data-route>${companion.type === 'audio' ? '聆聽本片配樂' : '觀看搭配影片'} ↗</a>` : external(demo.audio, '獨立配樂 ↗');
  app.innerHTML = `<div class="shell detail"><a class="back" href="${worksRoute}" data-route>← 作品集</a><div class="detail-heading"><div><p class="eyebrow">${escape(demo.type.toUpperCase())} / SKILL LIBRARY</p><h1 id="page-title">${escape(demo.title)}</h1><p class="subtitle">${escape(demo.subtitle || demo.summary)}</p></div><div class="facts">${facts(demo)}</div></div>${demo.editorialNote ? `<p class="editorial-note">${escape(demo.editorialNote)}</p>` : ''}${media ? media(demo) : '<p class="empty">此作品格式尚未支援。</p>'}
  <div class="player-controls">${['video','audio'].includes(demo.type) ? '<button class="cta" type="button" id="toggle-play">播放作品 ↗</button>' : external(demo.src, '在新頁面開啟 ↗', 'cta')}<div class="downloads">${demo.references?.length ? '<a href="#references">資料來源 ↘</a>' : ''}${companionLink}${external(demo.src, demo.type === 'audio' ? '下載音樂 ↗' : '下載／開啟作品 ↗')}${external(demo.download, '來源套件 ↗')}${external(demo.source, '製作專案 ↗')}</div></div>
  ${demo.chapters?.length && ['video','audio'].includes(demo.type) ? `<nav class="chapters" aria-label="選擇作品段落">${demo.chapters.map(chapter => `<button type="button" data-seek="${chapter.time}" aria-pressed="false"><span>${timecode(chapter.time)}</span>${escape(chapter.title)}</button>`).join('')}</nav>` : ''}
  <div class="detail-body"><div><h2>${escape(demo.summary)}</h2><p>${escape(demo.description)}</p></div><aside class="contributors"><h2>這件作品用到了</h2>${(demo.contributors ?? []).map(contributor => {const skill = skills.get(contributor.skillId); return skill ? `<a class="contributor" href="${route('skill', skill.id)}" data-route><strong>${escape(skill.name)} ↗</strong><span>${escape(contributor.role)}</span></a>` : '';}).join('')}<p class="credit">${escape(demo.credits || '')}</p><p class="credit">${external(demo.rights, '素材來源與授權 ↗')}</p></aside></div>${sourceNotes(demo)}</div>`;
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
  // Preserve links to the former homepage sections while giving the gallery its own route.
  if (!skill && !demo && ['#skills','#works'].includes(location.hash)) {
    const legacy = new URL(location.href);
    if (legacy.hash === '#works') {legacy.searchParams.set('view','works'); params.set('view','works');}
    legacy.hash = '';
    history.replaceState(null, '', legacy.href);
  }
  if (skill && skills.has(skill)) {skillPage(skills.get(skill)); document.title = `${skills.get(skill).name} — ${catalog.site.title}`; showLocation('skill',skills.get(skill));}
  else if (demo && demos.has(demo)) {demoPage(demos.get(demo)); document.title = `${demos.get(demo).title} — ${catalog.site.title}`; showLocation('demo',demos.get(demo));}
  else if (skill || demo) {app.innerHTML = '<div class="shell error"><h1 id="page-title">找不到這個項目</h1><p>它可能已更名，請從目錄選擇。</p><a href="./" data-route>回到 Skills 目錄 ↗</a></div>'; document.title = `找不到項目 — ${catalog.site.title}`; showLocation('error');}
  else if (params.get('view') === 'works') {worksPage(); document.title = `作品集 — ${catalog.site.title}`; showLocation('works');}
  else {home(); document.title = `${catalog.site.title} — ${catalog.site.owner}`; showLocation('home');}
  renderedRoute = location.pathname + location.search;
  app.setAttribute('aria-busy', 'false');
  animate();
  if (focus) {app.focus({preventScroll:true}); window.scrollTo({top:0, behavior:'instant'});}
  if (location.hash) {requestAnimationFrame(() => document.getElementById(location.hash.slice(1))?.scrollIntoView());}
}

document.addEventListener('click', event => {
  const link = event.target.closest('a[data-route]');
  if (!link || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
  if (!catalog) return;
  event.preventDefault();
  history.pushState(null, '', link.href);
  render(true);
});
window.addEventListener('popstate', () => {
  if (!catalog) return;
  if (renderedRoute === location.pathname + location.search && !['#skills','#works'].includes(location.hash)) {
    if (location.hash) document.getElementById(location.hash.slice(1))?.scrollIntoView();
    return;
  }
  render(true);
});
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
  app.innerHTML = '<div class="shell error"><h1>Skill 目錄暫時無法載入</h1><p>請重新整理，或直接查看 GitHub 專案。</p><a href="https://github.com/bigtongue5566">前往 GitHub ↗</a></div>';
  console.error('Skill catalog could not be loaded:', error.message);
}
