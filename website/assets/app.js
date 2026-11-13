/* Progressive enhancement. Every editorial page is readable without JavaScript. */
(() => {
  'use strict';
  const base = document.body.dataset.base || '';
  const form = document.querySelector('.search-form');
  const results = document.querySelector('#search-results');
  if (!form || !results) return;
  const input = form.querySelector('[name=q]');
  const platformFilter = document.querySelector('#filter-platform');
  const categoryFilter = document.querySelector('#filter-category');
  const featuredFilter = document.querySelector('#filter-featured');
  const browse = document.querySelector('#browse-content');
  const params = new URLSearchParams(location.search);
  const searchPage = /\/search\/$/.test(location.pathname);
  let platform = params.get('platform') || document.body.dataset.platform || '';
  let category = params.get('category') || document.body.dataset.category || '';
  let dataPromise;
  let requestId = 0;
  let timer;
  const h = (value) => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const normalize = value => value.toLocaleLowerCase().normalize('NFKC').replace(/\s+/g,' ').trim();
  const load = () => dataPromise || (dataPromise = fetch(`${base}/assets/catalog.json`).then(response => {
    if (!response.ok) throw new Error('catalog');
    return response.json();
  }).catch(error => { dataPromise = null; throw error; }));
  const updateURL = () => {
    const query = new URLSearchParams();
    if (input.value.trim()) query.set('q',input.value.trim());
    if (platform) query.set('platform',platform);
    if (category) query.set('category',category);
    if (featuredFilter?.checked) query.set('featured','1');
    history.replaceState(null,'',`${location.pathname}${query.size ? '?'+query : ''}`);
  };
  function renderCard(p, data) {
    const cat = data.categories.find(c => c.id === p.category);
    const href = !p.featured && platform ? p.targets[platform] : p.url;
    const external = p.featured ? '' : ' target="_blank" rel="noopener noreferrer"';
    const platforms = p.platforms.map(k => data.platforms[k]).join(' / ');
    const icon = /^[\x00-\x7F]/.test(p.name) ? p.name[0].toUpperCase() : p.name.slice(0,2);
    return `<article class="tool-card"><div class="card-top"><span class="app-icon tone-${data.categories.indexOf(cat)%6}" aria-hidden="true">${h(icon)}</span><div><h3><a href="${h(href)}"${external}>${h(p.name)}</a></h3><span class="eyebrow">${h(cat.name)}</span></div></div><p class="card-summary">${h(p.summary)}</p><div class="card-bottom"><span title="${h(platforms)}">${h(platforms)}</span><a class="card-action" href="${h(href)}"${external}>${p.featured?'了解与获取':'前往来源'}</a></div></article>`;
  }
  async function search() {
    const current = ++requestId;
    const query = normalize(input.value);
    const active = searchPage || query.length > 0 || Boolean(platformFilter && platform) || Boolean(categoryFilter && category) || Boolean(featuredFilter?.checked);
    results.hidden = !active;
    if (browse) browse.hidden = active;
    updateURL();
    if (!active) return;
    results.innerHTML = '<p class="muted">正在查找工具…</p>';
    try {
      const data = await load();
      if (current !== requestId) return;
      if (platform && !data.platforms[platform]) platform = '';
      if (category && !data.categories.some(c => c.id === category)) category = '';
      const terms = query.split(' ').filter(Boolean);
      let rows = data.products.filter(p => (!platform || p.platforms.includes(platform)) && (!category || p.category === category) && (!featuredFilter?.checked || p.featured));
      rows = rows.map(p => {
        const cat = data.categories.find(c => c.id === p.category);
        const name = normalize(p.name);
        const aliases = p.aliases.map(normalize);
        const text = normalize([p.name,p.summary,...p.aliases,cat.name,cat.terms].join(' '));
        let score = p.featured ? 10 : 0;
        if (!terms.every(t => text.includes(t))) return null;
        if (query && name === query) score += 100;
        else if (query && aliases.includes(query)) score += 80;
        else if (query && name.includes(query)) score += 60;
        return {p,score};
      }).filter(Boolean).sort((a,b) => b.score-a.score || a.p.name.localeCompare(b.p.name,'zh-CN')).map(row=>row.p);
      results.innerHTML = `<div class="results-heading"><div><h2>${query ? '搜索结果' : '浏览工具'} <span class="muted">${rows.length} 个</span></h2><p>${platform ? h(data.platforms[platform]) : '全部平台'}${category ? ' / '+h(data.categories.find(c=>c.id===category).name) : ''}</p></div><button type="button" class="button secondary" id="reset-search">重置筛选</button></div>`;
      if (!rows.length) {
        results.insertAdjacentHTML('beforeend',`<div class="empty"><h3>暂时没有找到合适的工具</h3><p>试试简短的名称或用途词，也可以切换平台和分类。</p><a class="text-link" href="${base}/categories/">浏览分类</a></div>`);
      } else {
        const grid = document.createElement('div');
        grid.className = 'tool-grid';
        results.append(grid);
        let shown = 0;
        const more = document.createElement('button');
        more.type = 'button'; more.className = 'load-more';
        function append() {
          grid.insertAdjacentHTML('beforeend',rows.slice(shown,shown+36).map(p=>renderCard(p,data)).join(''));
          shown = Math.min(shown+36,rows.length);
          more.textContent = `继续显示（${shown} / ${rows.length}）`;
          more.hidden = shown === rows.length;
        }
        more.addEventListener('click',append);
        append(); results.append(more);
      }
      document.querySelector('#reset-search').addEventListener('click',() => {
        input.value=''; platform=''; category='';
        form.querySelector('[name=platform]').value='';
        form.querySelector('[name=category]').value='';
        if (platformFilter) platformFilter.value='';
        if (categoryFilter) categoryFilter.value='';
        if (featuredFilter) featuredFilter.checked=false;
        search(); input.focus();
      });
    } catch (_) {
      if (current !== requestId) return;
      results.innerHTML = `<div class="empty"><h3>搜索目录暂时无法加载</h3><p>可以刷新后重试，也可以继续浏览静态目录。</p><a class="text-link" href="${base}/directory/">浏览完整目录</a></div>`;
    }
  }
  if (params.has('q')) input.value = params.get('q').slice(0,120);
  if (platformFilter) { platformFilter.value=platform; platformFilter.addEventListener('change',() => { platform=platformFilter.value; search(); }); }
  if (categoryFilter) { categoryFilter.value=category; categoryFilter.addEventListener('change',() => { category=categoryFilter.value; search(); }); }
  if (featuredFilter) { featuredFilter.checked=params.get('featured')==='1'; featuredFilter.addEventListener('change',search); }
  form.addEventListener('submit',event => { event.preventDefault(); clearTimeout(timer); search(); });
  input.addEventListener('input',() => { clearTimeout(timer); timer=setTimeout(search,180); });
  if (searchPage || input.value.trim() || (platformFilter && platform) || (categoryFilter && category) || featuredFilter?.checked) search();
  const suggestion = document.querySelector('#device-suggestion');
  if (suggestion) {
    const ua = navigator.userAgent;
    const detected = /Android/i.test(ua) ? 'android' : /iPhone|iPad/i.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints>1) ? 'ios' : /Windows/i.test(ua) ? 'windows' : /Mac/i.test(ua) ? 'darwin' : /Linux/i.test(ua) ? 'linux' : '';
    const names = {android:'Android',ios:'iPhone / iPad',windows:'Windows',darwin:'macOS',linux:'Linux'};
    if (detected) { suggestion.hidden=false; suggestion.innerHTML=`你可能正在使用 ${names[detected]}<a href="${base}/platform/${detected}/">查看对应平台的常用工具</a>`; }
  }
})();
