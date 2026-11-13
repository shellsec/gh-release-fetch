"""Build with: python -m website.build [--site-url https://tools.example.com]."""
import argparse
import html
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, quote
from xml.sax.saxutils import escape as xml_escape

from .catalog import ROOT, collect, safe_url
from .content import CATEGORIES, COLLECTIONS, PLATFORMS, PLATFORM_PICKS
from .downloads import refresh
from .brand_motion import add_brand_motion

HERE = Path(__file__).parent
NAME = '工具拾光'
REPO = 'https://github.com/shellsec/gh-release-fetch'
CATS = {c[0]: c for c in CATEGORIES}


def esc(value):
    return html.escape(str(value), quote=True)


def json_script(value):
    return json.dumps(value, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')


class Site:
    def __init__(self, output, url, products, downloads):
        self.out = output
        self.url = url.rstrip('/')
        self.base = urlsplit(url).path.rstrip('/') if url else ''
        self.products = products
        self.by_id = {p['id']: p for p in products}
        self.downloads = downloads
        self.routes = []

    def link(self, path=''):
        return f'{self.base}/{path.lstrip("/")}'

    def product_link(self, p):
        return self.link(f"app/{p['id']}/") if p['featured'] else next(iter(p['platforms'].values()))['url']

    def cards(self, products):
        result = []
        for p in products:
            category = CATS[p['category']]
            platforms = ' / '.join(PLATFORMS[k][0] for k in p['platforms'])
            href = self.product_link(p)
            external = '' if p['featured'] else ' target="_blank" rel="noopener noreferrer"'
            result.append(f'''<article class="tool-card">
<div class="card-top"><span class="app-icon tone-{list(CATS).index(p['category']) % 6}" aria-hidden="true">{esc(p['name'][:2] if not p['name'][0].isascii() else p['name'][0].upper())}</span>
<div><h3><a href="{esc(href)}"{external}>{esc(p['name'])}</a></h3><span class="eyebrow">{esc(category[1])}</span></div></div>
<p class="card-summary">{esc(p['summary'])}</p>
<div class="card-bottom"><span title="{esc(platforms)}">{esc(platforms)}</span><a class="card-action" href="{esc(href)}"{external}>{'了解与获取' if p['featured'] else '前往来源'}</a></div></article>''')
        return '<div class="tool-grid">' + ''.join(result) + '</div>' if result else '<div class="empty"><h3>这个平台暂未收录相关工具</h3><p>可以切换其他平台，或从完整目录继续查找。</p></div>'

    def section(self, title, subtitle, body, extra=''):
        return f'<section class="section"><div class="section-heading"><div><h2>{title}</h2><p>{subtitle}</p></div>{extra}</div>{body}</section>'

    def collections(self):
        return '<div class="collection-grid">' + ''.join(f'''<a class="collection" href="{self.link('collections/'+c['id']+'/')}"><span aria-hidden="true">{c['icon']}</span><div><h3>{c['name']}</h3><p>{c['intro']}</p></div></a>''' for c in COLLECTIONS) + '</div>'

    def category_tiles(self):
        return '<div class="category-grid">' + ''.join(f'''<a href="{self.link('category/'+c[0]+'/')}"><span aria-hidden="true">{c[3]}</span><h3>{c[1]}</h3><p>{c[2]}</p></a>''' for c in CATEGORIES) + '</div>'

    def platforms(self, active=''):
        primary = ['windows','darwin','linux','android','ios']
        links = f'<a class="platform-chip {"active" if not active else ""}" href="{self.link()}">全部平台</a>'
        links += ''.join(f'<a class="platform-chip {"active" if active == id else ""}" href="{self.link("platform/"+id+"/")}" {"aria-current=page" if active == id else ""}>{esc(PLATFORMS[id][0])}</a>' for id in primary)
        other = ''.join(f'<a href="{self.link("platform/"+id+"/")}">{p[0]}</a>' for id,p in PLATFORMS.items() if id not in primary)
        return f'<nav class="platforms" aria-label="选择平台">{links}<details class="more-platforms"><summary>电视与游戏设备</summary><div>{other}</div></details></nav>'

    def search_form(self, value='', platform='', category=''):
        return f'''<form class="search-form" action="{self.link('search/')}" role="search"><label class="sr-only" for="search-input">搜索工具名称或用途</label><span aria-hidden="true">⌕</span><input id="search-input" name="q" type="search" value="{esc(value)}" placeholder="搜软件，或试试“截图”“传照片”“解压”" autocomplete="off" maxlength="120"><input type="hidden" name="platform" value="{esc(platform)}"><input type="hidden" name="category" value="{esc(category)}"><button type="submit">找工具</button></form><div class="search-examples">试试用途搜索：<a href="{self.link('search/?q='+quote('传照片'))}">传照片</a><a href="{self.link('search/?q='+quote('录屏'))}">录屏</a><a href="{self.link('search/?q='+quote('PDF'))}">PDF</a><a href="{self.link('search/?q='+quote('本地模型'))}">本地模型</a></div>'''

    def filters(self, *, platform=False, category=False):
        fields = ''
        if platform:
            options = ''.join(f'<option value="{k}">{v[0]}</option>' for k,v in PLATFORMS.items())
            fields += f'<label>筛选平台<select id="filter-platform"><option value="">全部平台</option>{options}</select></label>'
        if category:
            options = ''.join(f'<option value="{c[0]}">{c[1]}</option>' for c in CATEGORIES)
            fields += f'<label>筛选分类<select id="filter-category"><option value="">全部分类</option>{options}</select></label>'
        return '<div class="search-filters">'+fields+'<label class="checkbox-label"><input type="checkbox" id="filter-featured">只看精选</label></div>'

    def page(self, path, title, description, body, *, platform='', category='', index=True, schema=None, crumbs=()):
        route = path.strip('/') + '/' if path.strip('/') else ''
        filename = self.out / route / 'index.html'
        filename.parent.mkdir(parents=True, exist_ok=True)
        canonical = self.url + '/' + route if self.url else ''
        metadata = f'<link rel="canonical" href="{esc(canonical)}"><meta property="og:url" content="{esc(canonical)}">' if canonical else ''
        graph = [{'@type':'WebSite', 'name':NAME, 'inLanguage':'zh-CN', **({'url':self.url+'/'} if self.url else {})}]
        if schema:
            graph.append(schema)
        if crumbs and self.url:
            graph.append({'@type':'BreadcrumbList', 'itemListElement':[{'@type':'ListItem','position':i+1,'name':label,'item':self.url+'/'+href} for i,(label,href) in enumerate([(NAME,''),*crumbs])]})
        sidebar = ''.join(f'<a class="{"selected" if c[0] == category else ""}" href="{self.link("category/"+c[0]+"/")}"><span aria-hidden="true">{c[3]}</span>{c[1]}</a>' for c in CATEGORIES)
        breadcrumb = '<nav class="breadcrumbs" aria-label="面包屑"><a href="'+self.link()+'">首页</a>'+''.join(f'<span aria-hidden="true">/</span><a href="{self.link(href)}">{esc(label)}</a>' for label,href in crumbs)+'</nav>' if crumbs else ''
        document = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · {NAME}</title><meta name="description" content="{esc(description)}"><meta name="robots" content="{'index,follow' if index else 'noindex,follow'}">
{metadata}<meta property="og:type" content="website"><meta property="og:locale" content="zh_CN"><meta property="og:site_name" content="{NAME}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta name="twitter:card" content="summary"><meta name="theme-color" content="#245edb">
<link rel="icon" href="{self.link('assets/favicon.svg')}" type="image/svg+xml"><link rel="stylesheet" href="{self.link('assets/style.css')}"><script type="application/ld+json">{json_script({'@context':'https://schema.org','@graph':graph})}</script>
<script src="{self.link('assets/app.js')}" defer></script></head>
<body data-base="{esc(self.base)}" data-platform="{esc(platform)}" data-category="{esc(category)}"><a class="skip-link" href="#main">跳到主要内容</a>
<header class="site-header"><a class="brand" href="{self.link()}"><span class="brand-mark" aria-hidden="true">拾</span><span>{NAME}<small>找到好用的那一个</small></span></a><nav aria-label="主导航"><a href="{self.link()}">发现工具</a><a href="{self.link('categories/')}">全部分类</a><a href="{self.link('collections/')}">场景清单</a><a href="{self.link('guide/')}">使用帮助</a></nav><a class="repo-link" href="{REPO}" target="_blank" rel="noopener noreferrer">GitHub 项目</a></header>
<div class="site-layout"><aside class="sidebar"><p class="sidebar-label">按用途找工具</p><nav aria-label="工具分类">{sidebar}</nav><a class="sidebar-all" href="{self.link('directory/')}">浏览完整目录</a><div class="sidebar-note">按需选择工具<br>让设备更好用一点。</div></aside>
<main id="main">{breadcrumb}{body}</main></div>
<footer><div><strong>{NAME}</strong><p>按平台与用途，找到适合自己的软件。</p></div><div><a href="{self.link('guide/')}">来源与获取说明</a><a href="{REPO}/issues" target="_blank" rel="noopener noreferrer">反馈与收录建议</a><p>独立软件导航，产品名称与商标归各自所有者。</p></div></footer>
</body></html>'''
        filename.write_text(document, encoding='utf-8')
        if index:
            self.routes.append(route)

    def listings(self):
        featured = [p for p in self.products if p['featured']]
        home_ids = PLATFORM_PICKS['windows']
        home_picks = [self.by_id[id] for id in home_ids]
        hero = f'''<section class="hero"><div class="hero-copy"><span class="hero-kicker">你的多平台工具指南</span><h1>好用的工具，<br>从这里找到。</h1><p>按设备选，按用途找。看懂工具能做什么，再获取适合你的版本。</p></div><div class="hero-illustration" aria-hidden="true"><div class="mini-window"><i></i><i></i><i></i><div class="mini-tools"><b>⇄</b><b>▤</b><b>▷</b><b>✎</b><b>⌨</b><b>◇</b></div><span>日常所需，各有好工具</span></div><div class="floating-label">找到 · 了解 · 获取</div></div></section>{self.search_form()}{self.platforms()}<p id="device-suggestion" class="device-suggestion" hidden></p>'''
        body = hero + '<div id="search-results" hidden aria-live="polite"></div><div id="browse-content">'
        body += self.section('从这些常用工具开始', '先看用途，再挑适合自己的。这里展示 Windows 常用精选，可在上方切换平台。', self.cards(home_picks), '<a class="text-link" href="'+self.link('directory/')+'">查看完整目录</a>')
        body += self.section('你想完成什么？', '把工具放进真实任务里，选择更简单。', self.collections())
        body += f'''<section class="section"><a class="collection" href="{self.link('tools/brand-motion/')}"><span aria-hidden="true">▷</span><div><h3>品牌动图工作台</h3><p>准备 Images 2.6 分镜提示词，把品牌分镜图预览并导出为循环 GIF。</p></div></a></section>'''
        body += self.section('按分类慢慢逛', '从日常办公到专业创作，每类都有清晰的用途介绍。', self.category_tiles())+'</div>'
        self.page('', '多平台常用软件推荐与工具下载导航', '发现 Windows、macOS、Linux、Android 和 iPhone 常用工具。按分类与场景搜索软件，查看用途介绍和官方获取入口。', body)
        for platform,(name,intro,_) in PLATFORMS.items():
            picks = [self.by_id[id] for id in PLATFORM_PICKS.get(platform,[]) if platform in self.by_id[id]['platforms']]
            rows = [p for p in self.products if platform in p['platforms']]
            heading = '常用精选' if picks else '设备工具与项目入口'
            body = f'<div class="page-intro"><h1>{name} 工具指南</h1><p>{intro}</p></div>{self.search_form(platform=platform)}{self.platforms(platform)}{self.filters(category=True)}<div id="search-results" hidden aria-live="polite"></div><div id="browse-content">'
            if picks:
                body += self.section(heading, '每种用途按需选择。系统自带功能够用时，可以直接使用。', self.cards(picks))
            body += self.section(f'{name} 收录目录', f'共 {len(rows)} 个产品；精选之外的项目请先阅读其来源说明。', self.cards(rows[:24]), f'<a class="text-link" href="{self.link("directory/"+platform+"/")}">浏览全部 {len(rows)} 个</a>')+'</div>'
            self.page(f'platform/{platform}', f'{name} 常用工具与软件下载指南', intro, body, platform=platform, crumbs=[(name,f'platform/{platform}/')])
        for id,name,intro,symbol,_,_ in CATEGORIES:
            rows = [p for p in self.products if p['category']==id]
            picks = [p for p in rows if p['featured']]
            body = f'<div class="page-intro"><span class="category-emblem" aria-hidden="true">{symbol}</span><h1>{name}</h1><p>{intro}</p></div>{self.search_form(category=id)}{self.filters(platform=True)}<div id="search-results" hidden aria-live="polite"></div><div id="browse-content">'
            body += self.section('先从这些工具了解', '按用途挑选；进入介绍页查看支持平台、获取方式与使用条件。', self.cards(picks) if picks else '<p>本类工具用途较专门，请先根据项目说明确认适用场景。</p>')
            body += self.section('更多收录', '这里同时包含软件、在线服务与项目资料；获取方式以来源页面为准。', self.cards([p for p in rows if not p['featured']][:24]), f'<a class="text-link" href="{self.link("search/?category="+id)}">搜索本类全部工具</a>')+'</div>'
            self.page(f'category/{id}', f'{name}工具推荐与获取指南', intro, body, category=id, crumbs=[(name,f'category/{id}/')])
        self.page('categories', '软件分类导航', '按用途浏览办公、文件、AI、开发、设计和多媒体工具。', '<div class="page-intro"><h1>每种用途，都有好工具</h1><p>先确定要完成什么，再选择合适的软件。</p></div>'+self.category_tiles(), crumbs=[('全部分类','categories/')])
        self.page('collections', '按场景选择工具', '从新电脑装机、办公学习到内容创作，查看按任务整理的软件清单。', '<div class="page-intro"><h1>工具，放进生活里</h1><p>按正在做的事情，找到一组合适的工具。</p></div>'+self.collections(), crumbs=[('场景清单','collections/')])
        for c in COLLECTIONS:
            rows = [self.by_id[id] for id in c['tools']]
            body = f'<div class="page-intro"><h1>{c["name"]}</h1><p>{c["intro"]}</p></div><div class="notice">这是一份按需选用的清单，不需要全部安装。进入工具详情后选择你的平台。</div>'+self.cards(rows)
            self.page('collections/'+c['id'], c['name']+'软件清单', c['intro'], body, crumbs=[('场景清单','collections/'),(c['name'],'collections/'+c['id']+'/')])
        self.directory()

    def directory(self):
        for platform in ['',*PLATFORMS]:
            rows = [p for p in self.products if not platform or platform in p['platforms']]
            prefix = 'directory/' + (platform+'/' if platform else '')
            pages = max(1,(len(rows)+59)//60)
            for page in range(pages):
                route = prefix + (f'page/{page+1}/' if page else '')
                nav = '<nav class="pagination" aria-label="目录翻页">'
                if page:
                    nav += f'<a href="{self.link(prefix+(f"page/{page}/" if page>1 else ""))}">上一页</a>'
                nav += f'<span>第 {page+1} / {pages} 页</span>'
                if page+1<pages:
                    nav += f'<a href="{self.link(prefix+f"page/{page+2}/")}">下一页</a>'
                nav += '</nav>'
                body = f'<div class="page-intro"><h1>{PLATFORMS[platform][0] if platform else "全部平台"}完整目录</h1><p>共 {len(rows)} 个产品。目录来自项目清单，具体支持情况与获取方式请阅读来源说明。</p></div>{self.search_form(platform=platform)}<div id="search-results" hidden aria-live="polite"></div><div id="browse-content">{nav}{self.cards(rows[page*60:(page+1)*60])}{nav}</div>'
                self.page(route, '软件完整目录', '浏览已收录的软件、服务与项目入口。', body, platform=platform, index=False, crumbs=[('完整目录',prefix)])

    def details(self):
        for p in self.products:
            if not p['featured']:
                continue
            cat = CATS[p['category']]
            record = self.downloads.get(p['id'], {})
            # A snapshot older than 48 hours must not be presented as current.
            try:
                age = (datetime.now(timezone.utc)-datetime.fromisoformat(record['fetched'])).total_seconds()
                if age < 0 or age > 48*3600:
                    record = {}
            except (KeyError,ValueError,TypeError):
                record = {}
            targets = ''
            for platform,target in p['platforms'].items():
                kind = '打开 App Store' if target['kind']=='store' and platform=='ios' else '打开应用商店' if target['kind']=='store' else '前往官方获取页'
                options = ''
                for asset in record.get('assets',[]):
                    if asset['platform'] != platform or not safe_url(asset['url']):
                        continue
                    options += f'<li><a href="{esc(asset["url"])}" rel="noopener noreferrer" target="_blank"><strong>{esc(asset["arch"])}</strong><span>{esc(asset["name"])}</span><b>下载安装包</b></a></li>'
                downloads = f'<p class="version-note">稳定版 {esc(record.get("version",""))} · 索引获取时间 {esc(record.get("fetched",""))}。请按 CPU 架构及系统要求选择；未进行实机安装验证。</p><ul class="asset-list">{options}</ul>' if options else '<p class="muted">从官方页面选择适合设备的版本与安装方式。</p>'
                hint = '<p class="platform-hint">Apple Silicon 与 Intel 使用不同版本时，请先在“关于本机”确认芯片。</p>' if platform=='darwin' else '<p class="platform-hint">按发行版选择官方支持的安装方式；不要仅凭文件扩展名安装。</p>' if platform=='linux' else '<p class="platform-hint">移动端功能与桌面端可能不同，商店可用性受地区与系统版本影响。</p>' if platform=='ios' else ''
                targets += f'<section class="target" id="get-{platform}"><h3>{PLATFORMS[platform][0]}</h3>{hint}{downloads}<a class="button secondary" href="{esc(target["url"])}" rel="noopener noreferrer" target="_blank">{kind}</a></section>'
            target_links = ''.join(f'<a href="#get-{k}">{PLATFORMS[k][0]}</a>' for k in p['platforms'])
            alternatives = [a for a in self.products if a['featured'] and a['category']==p['category'] and a['id']!=p['id']][:3]
            body = f'''<section class="product-hero"><span class="app-icon large tone-{list(CATS).index(p['category'])%6}" aria-hidden="true">{esc(p['name'][0].upper())}</span><div><a class="eyebrow" href="{self.link('category/'+p['category']+'/')}">{cat[1]}</a><h1>{esc(p['name'])}</h1><p>{esc(p['summary'])}</p></div></section>
<div class="detail-layout"><div><section class="detail-panel"><h2>为什么可以选它</h2><p>{esc(p['reason'])}</p><h3>适合谁</h3><p>{esc(p['audience'])}</p>{f'<div class="notice">{esc(p["note"])}</div>' if p['note'] else ''}</section><section class="detail-panel"><h2>选择你的平台</h2><p>先确认设备平台，再查看安装包或官方获取方式。</p><nav class="target-links" aria-label="跳到对应平台">{target_links}</nav>{targets}</section></div><aside class="product-aside"><h2>获取前看一眼</h2><p>优先稳定版本，并确认最低系统要求。浏览器无法可靠判断你的 CPU 架构。</p><p>按钮会前往官方渠道或项目发布的安装包；软件费用与服务规则以官方说明为准。</p><a href="{esc(p['official'])}" rel="noopener noreferrer" target="_blank">访问官方网站</a><a href="{self.link('guide/')}">了解下载与更新</a></aside></div>'''
            if alternatives:
                body += self.section('同类工具，也可以看看', '用途可能不同，按自己的任务选择。', self.cards(alternatives))
            schema = {'@type':'SoftwareApplication','name':p['name'],'description':p['summary'],'applicationCategory':cat[1],'operatingSystem':', '.join(PLATFORMS[k][0] for k in p['platforms']),'sameAs':p['official']}
            self.page('app/'+p['id'], p['name']+'：用途介绍与官方获取入口', p['summary']+' '+p['reason'], body, category=p['category'], schema=schema, crumbs=[(cat[1],'category/'+cat[0]+'/'),(p['name'],'app/'+p['id']+'/')])

    def supporting(self):
        body = f'''<div class="page-intro"><h1>找到适合你的工具</h1><p>支持软件名称、别名和用途，例如“传照片”“解压”“录屏”。</p></div>{self.search_form()}{self.filters(platform=True,category=True)}<div id="search-results" aria-live="polite"></div><noscript><div class="notice">即时搜索需要启用 JavaScript。你仍可浏览下方目录和分类页面。</div></noscript><div id="browse-content">{self.section('先看看常用精选','也可以按平台和分类浏览。',self.cards([p for p in self.products if p['featured']][:12]))}<a class="text-link" href="{self.link('directory/')}">浏览完整目录</a></div>'''
        self.page('search','搜索软件与用途','按软件名称和用途查找适合各平台的工具。',body,index=False)
        body = '''<div class="page-intro"><h1>找到工具之后，怎么获取？</h1><p>知道入口从哪里来，也知道下一步该做什么。</p></div><div class="guide-grid">
<section class="detail-panel"><h2>先选平台，再选架构</h2><p>Windows、Mac 和 Linux 的安装方式不同。x64、ARM64 等版本也不能随意混用；不确定时先查看设备的系统信息。</p></section>
<section class="detail-panel"><h2>按钮分别表示什么</h2><p>“下载安装包”指向项目发布的文件；“前往官方获取页”由官网提供版本选择；“打开 App Store”进入官方商店；“前往来源”可能是软件、服务或项目说明。</p></section>
<section class="detail-panel"><h2>版本与更新</h2><p>可解析的精选项目由构建任务获取稳定版索引；页面显示索引时间。没有可确认的安装包时提供官方入口。网站不会自动更新你电脑上已经安装的软件。</p></section>
<section class="detail-panel"><h2>系统自带功能也很好用</h2><p>截图、备份、密码管理与基础文件操作，系统通常已经提供部分能力。只有需要更多功能时，再安装第三方工具。</p></section>
<section class="detail-panel"><h2>清单与精选有什么区别</h2><p>精选有单独整理的用途、推荐理由和平台范围；完整目录来自项目软件清单，可能包含进阶项目或尚需配置的条目。收录不表示逐个完成安装测试。</p></section>
<section class="detail-panel"><h2>来源与费用</h2><p>工具信息来自项目清单与官方网站。我们不提供修改版安装包，不虚构评分和下载量。免费软件、开源软件与免费在线服务不是同一概念，费用与许可请阅读官方条款。</p></section></div>'''
        self.page('guide','软件获取与更新说明','了解软件下载入口、平台架构、版本更新和信息来源。',body,crumbs=[('使用帮助','guide/')])
        self.page('404','页面没有找到','返回分类或搜索工具。',f'<div class="empty"><h1>这条路径没有找到工具</h1><p>可以回到首页，或继续搜索你需要的软件。</p><a class="button" href="{self.link()}">返回首页</a></div>',index=False)
        shutil.copyfile(self.out/'404/index.html',self.out/'404.html')

    def metadata(self):
        (self.out/'.nojekyll').touch()
        robots = 'User-agent: *\nAllow: /\n'
        if self.url:
            robots += f'Sitemap: {self.url}/sitemap.xml\n'
            urls = ''.join(f'<url><loc>{xml_escape(self.url+"/"+route)}</loc></url>' for route in self.routes)
            (self.out/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+urls+'</urlset>',encoding='utf-8')
        (self.out/'robots.txt').write_text(robots,encoding='utf-8')
        payload = {'categories':[dict(id=c[0],name=c[1],description=c[2],symbol=c[3],terms=c[5]) for c in CATEGORIES], 'platforms':{k:v[0] for k,v in PLATFORMS.items()}, 'products':[]}
        for p in self.products:
            payload['products'].append({**{k:p[k] for k in ('id','name','summary','category','aliases','featured')},'platforms':list(p['platforms']),'url':self.product_link(p),'targets':{k:v['url'] for k,v in p['platforms'].items()}})
        (self.out/'assets/catalog.json').write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')),encoding='utf-8')


def build(output, site_url='', *, refresh_downloads=False):
    if site_url:
        parsed = urlsplit(site_url)
        if not safe_url(site_url) or parsed.query or parsed.fragment or re.search(r'[^a-zA-Z0-9/_:.-]', site_url):
            raise ValueError('site-url must be an http(s) origin with an optional ASCII path')
    output = Path(output).resolve()
    # No recursive deletion: rebuilding only replaces generated files.
    output.mkdir(parents=True,exist_ok=True)
    shutil.copytree(HERE/'assets',output/'assets',dirs_exist_ok=True)
    products = collect()
    cache_path = output/'downloads.json'
    records = json.loads(cache_path.read_text(encoding='utf-8')) if cache_path.exists() else {}
    if refresh_downloads:
        records, errors = refresh(products,cache_path)
        for error in errors:
            print('Official-page fallback:',error)
    site = Site(output,site_url,products,records)
    site.listings()
    site.details()
    site.supporting()
    add_brand_motion(site)
    site.metadata()
    if not site_url and (output/'sitemap.xml').exists():
        (output/'sitemap.xml').unlink()
    print(f'Built {len(site.routes)} indexable pages, {len(products)} products -> {output}')
    return site


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'dist/site')
    parser.add_argument('--site-url',default='')
    parser.add_argument('--refresh-downloads',action='store_true')
    args = parser.parse_args()
    build(args.output,args.site_url,refresh_downloads=args.refresh_downloads)


if __name__ == '__main__':
    main()
