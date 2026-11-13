"""The browser-based brand motion tool and its instructions."""


def add_brand_motion(site):
    body = f'''
<div class="page-intro">
  <h1>品牌动图工作台</h1>
  <p>把同一件产品或吉祥物做成循环 GIF。从一张定稿出发，固定识别细节，只改动作。</p>
</div>
<div class="motion-grid" id="brand-motion" hidden>
  <section class="detail-panel">
    <h2>准备分镜提示词</h2>
    <label>主体与必须保留的细节<textarea id="motion-subject" rows="3" maxlength="600">工具拾光的蓝色工具盒。保留 #245EDB 主色、圆角轮廓和正面的白色四格标记。</textarea></label>
    <label>本轮动作<textarea id="motion-action" rows="2" maxlength="400">上方把手轻轻抬起，再回到初始位置。</textarea></label>
    <p>把下面的提示词和你的品牌定稿一起交给 ChatGPT 或 Codex。下一轮继续使用同一张定稿，并附上上一版分镜。</p>
    <textarea id="motion-prompt" rows="8" aria-label="分镜提示词" readonly></textarea>
    <button type="button" class="button secondary" id="motion-copy">复制提示词</button>
    <span id="motion-copy-status" role="status"></span>
  </section>
  <section class="detail-panel">
    <h2>预览并导出 GIF</h2>
    <form id="motion-form">
      <fieldset id="motion-controls">
        <label>选择分镜图<input id="motion-file" type="file" accept="image/png,image/jpeg,image/webp"></label>
        <div class="motion-settings">
          <label>列数<input id="motion-columns" type="number" min="1" max="8" value="3" required></label>
          <label>行数<input id="motion-rows" type="number" min="1" max="8" value="2" required></label>
          <label>每帧毫秒<input id="motion-delay" type="number" min="50" max="2000" step="10" value="180" required></label>
        </div>
        <p>从左到右、从上到下读取。支持 2–16 帧等尺寸网格、最大 12 MB。图片在本机浏览器处理。</p>
        <p>导出时每帧长边最多 320 像素，颜色会压缩至 256 色，透明区域会填白。</p>
        <div class="motion-actions">
          <button class="button" type="submit">生成 GIF</button>
          <button class="button secondary" id="motion-demo" type="button">试用工具拾光样例</button>
        </div>
      </fieldset>
    </form>
    <p id="motion-status" role="status"></p>
    <div id="motion-result" hidden>
      <img id="motion-preview" alt="导出的 GIF 预览">
      <div class="motion-actions">
        <button class="button secondary" id="motion-play" type="button">播放预览</button>
        <a class="button" id="motion-download" download="brand-motion.gif">下载 GIF</a>
      </div>
    </div>
  </section>
</div>
<noscript><p class="notice">启用 JavaScript 后即可预览和导出 GIF。</p></noscript>
<section class="detail-panel">
  <h2>Images 2.6 怎么用在品牌素材上？</h2>
  <p>首轮定稿保留为参考图。编辑时标明要改的区域，逐帧检查标记、配色、轮廓和产品比例。需要精确保留的字标，适合在定稿后使用原始品牌素材叠加。</p>
  <p>Images API 的生成端点可以直接输出 GIF。需要先多轮修改时，可把静态分镜定稿后导入本工具，核对顺序并导出。直接拿到 GIF 时可以跳过分镜转换。<a class="text-link" href="https://developers.openai.com/api/docs/guides/image-generation#generate-animated-gif-output">OpenAI API 文档</a></p>
</section>
<script type="module" src="{site.link('assets/brand-motion.js')}"></script>'''
    site.page(
        'tools/brand-motion', '品牌动图工作台与分镜 GIF 转换',
        '为 Images 2.6 准备品牌分镜提示词，在浏览器本地预览并将等尺寸分镜图导出为循环 GIF。',
        body, crumbs=[('品牌动图工作台', 'tools/brand-motion/')],
    )
