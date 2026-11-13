# 工具拾光 · 多平台软件导航站

网站独立放在 `website/`，复用同一仓库的软件清单，不改变本地下载工具。
品牌名称为本次开发使用的暂定名称，可在 `build.py` 的 `NAME` 修改。

## 本地预览

在仓库根目录运行，Python 3.10+，无额外运行依赖：

```powershell
python -m website.build
python -m http.server 8080 --bind 127.0.0.1 --directory dist/site
```

打开 http://127.0.0.1:8080/ 。不要直接双击 HTML，即时搜索需要 HTTP 服务加载索引。
本地构建没有正式域名时不生成虚构 canonical 和 sitemap。

正式构建示例（域名仅为示例，替换为自己的域名）：

```powershell
python -m website.build --site-url https://tools.example.com --refresh-downloads
```

`--site-url` 也支持 `https://owner.github.io/repo` 这样的子路径，页面链接和资源随之调整。
域名变更后务必重新构建。构建输出不要直接人工编辑。若删除产品或更改路径，应使用全新的输出目录，避免旧产物残留；Actions 每次都从干净目录生成。

## 当前能力

- 12 个平台入口、18 个分类入口、7 个场景清单和 41 个精选产品。
- 精选产品合并平台差异，独立详情页介绍用途、适合人群和官方获取方式。
- 清单目录与即时搜索：名称、别名、用途词、平台、分类、只看精选、分批显示。
- 不依赖 JavaScript 的首页、平台页、分类页、专题、详情及分页完整目录。
- SEO：独立标题与描述、canonical、Open Graph、Twitter Card、面包屑和软件结构化数据、sitemap、robots、404。搜索与完整原始目录不索引；不编造评分和价格。
- 可选获取精选项目 GitHub 最新稳定 Release 的安装包列表，按明确的平台与架构展示；无法确认时提供官网入口。

完整目录条目没有单独生成介绍页，避免仅凭原始技术简介制造大量低信息页面。

## 编辑内容

- `content.py`：分类说明、精选产品、平台范围、推荐理由、场景清单及平台精选。
- `catalog.py`：从 `apps/`、手机、电视、掌机和主机目录读取公开字段，排除个人配置与原始下载运行参数。
- `build.py`：静态 HTML、SEO、目录和搜索索引生成。
- `downloads.py`：可选的构建时 GitHub 稳定版解析。
- `assets/`：本地 CSS、JS、SVG 图标。工具方块是文字缩略标识，不冒充官方图标。

新增精选：在 `FEATURED` 增加产品，明确平台支持，补充用途、推荐理由和官方地址，再按需放入平台/专题清单。`aliases` 可关联不同平台的旧 ID；不要凭同仓库地址合并不同产品。
所有精选来自人工整理的首批候选，收录不代表每个平台完成了实机验证。价格、最低系统要求和具体功能以官网为准。

## 下载与版本维护

默认构建不联网，全部产品都保留官网或商店入口。
`--refresh-downloads` 仅查询精选中声明了官方仓库的项目，不扫描全部目录。
环境变量 `GITHUB_TOKEN` 可增加 API 配额；令牌不会写入站点产物或页面。

只接受最新非预发布 Release 中能识别平台与 CPU 架构的安装文件；排除源码、调试、未签名等文件，不猜测归档格式和缺失架构。
解析结果是上游发布索引，不表示实机验证或下载完成。失败回退官网；超过 48 小时的快照不显示直接下载。
下载按钮不运行程序，也不自动更新已安装软件。非 GitHub 项目目前提供官方版本选择页。

## GitHub Pages 与域名

1. 将代码推送到默认分支（本仓库当前为 `master`，workflow 据此监听；更改默认分支时请同步调整）。
2. 仓库 Settings → Pages → Build and deployment 选择 GitHub Actions。
3. 运行 `Software directory website` workflow。它会测试、构建并部署 `dist/site/`。
4. Pages 的 Custom domain 填入子域名，例如 `tools.你的域名`，按 GitHub 提供的要求配置 DNS，再启用 HTTPS。
5. 在仓库 Variables 中设置 `WEBSITE_SITE_URL=https://tools.你的域名`，重新运行 workflow，统一 canonical、sitemap 和分享链接。
6. 在 Google Search Console 等站长平台验证域名、提交 `/sitemap.xml`；是否收录与排名由搜索引擎决定。

绑定自定义域名的配置在 Pages 设置中完成，workflow 不擅自写入占位域名或替换现有 DNS。
每天每六小时刷新一次索引并部署；API 故障会使用官方入口，不阻断整个网站生成。schedule 在非默认分支不运行。
若仓库已有其他 Pages 网站，请先合并部署路径再启用本 workflow，避免覆盖既有站点。

## 验证

```powershell
python -m unittest discover -s tests -p test_website.py
node --check website/assets/app.js
```

测试检查平台合并、危险 URL、源码/架构排除、静态详情、SEO、子路径资源及全站内链。

可选真实浏览器验证：在具备 Playwright 与 Chrome 的开发环境中，保持本地预览服务运行，执行 `node tests/website_browser.cjs`。可追加站点地址参数；截图保存在忽略提交的 `website/.preview/`，不增加网站运行依赖。

参考：[GitHub Pages 自定义工作流](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)、[Google 软件结构化数据](https://developers.google.com/search/docs/appearance/structured-data/software-app)、[Sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)。基础结构化数据不保证软件富媒体搜索结果资格；没有真实价格和评价就不补造这些字段。
