/* Optional browser verification: NODE_PATH must expose playwright. No runtime dependency. */
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

(async () => {
  const origin = (process.argv[2] || 'http://127.0.0.1:8080').replace(/\/$/, '');
  const browser = await chromium.launch({channel:process.env.PLAYWRIGHT_CHANNEL || 'chrome',headless:true});
  const context = await browser.newContext({viewport:{width:1440,height:1050}});
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  const preview = path.resolve('website/.preview');
  fs.mkdirSync(preview,{recursive:true});
  try {
    await page.goto(origin+'/',{waitUntil:'networkidle'});
    assert.match(await page.title(),/工具拾光/);
    assert.equal(await page.locator('#browse-content .tool-card').count(),12);
    await page.screenshot({path:path.join(preview,'desktop.png'),fullPage:true});
    await page.getByRole('searchbox').fill('传照片');
    await page.locator('#search-results .tool-card').first().waitFor();
    assert.match(await page.locator('#search-results .tool-card').first().innerText(),/LocalSend/);
    await page.getByRole('searchbox').fill('<img src=x onerror=alert(1)>');
    await page.locator('#search-results .empty').waitFor();
    assert.equal(await page.locator('#search-results img').count(),0);

    await page.goto(origin+'/search/?q=localsend&platform=ios&category=transfer',{waitUntil:'networkidle'});
    await page.locator('#search-results .tool-card').first().waitFor();
    assert.match(await page.locator('#search-results .tool-card').first().innerText(),/LocalSend/);
    assert.equal(await page.locator('#filter-platform').inputValue(),'ios');
    await page.locator('#filter-platform').selectOption('windows');
    await page.locator('#filter-category').selectOption('files');
    await page.getByRole('searchbox').fill('7zip');
    await page.locator('#search-results .tool-card').first().waitFor();
    await page.waitForFunction(() => document.querySelector('#search-results .tool-card')?.textContent.includes('7-Zip'));
    await page.locator('#filter-platform').selectOption('ios');
    await page.locator('#search-results .empty').waitFor();

    await page.goto(origin+'/category/office/',{waitUntil:'networkidle'});
    await page.locator('#filter-platform').selectOption('windows');
    await page.locator('#search-results .tool-card').first().waitFor();
    assert.match(await page.locator('#search-results').innerText(),/LibreOffice/);
    await page.goto(origin+'/platform/android/',{waitUntil:'networkidle'});
    await page.locator('#filter-category').selectOption('transfer');
    await page.locator('#search-results .tool-card').first().waitFor();
    assert.match(await page.locator('#search-results').innerText(),/LocalSend/);

    await page.goto(origin+'/app/localsend/',{waitUntil:'networkidle'});
    assert.equal(await page.locator('h1').innerText(),'LocalSend');
    assert.match(await page.locator('#get-ios a').last().getAttribute('href'),/^https:\/\/apps.apple.com\//);
    const schema = JSON.parse(await page.locator('script[type="application/ld+json"]').textContent());
    assert(schema['@graph'].some(item=>item['@type']==='SoftwareApplication'));
    await page.screenshot({path:path.join(preview,'detail.png'),fullPage:true});
    for (const width of [360,390,768,1280,1440]) {
      await page.setViewportSize({width,height:900});
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,`detail overflow at ${width}`);
      await page.goto(origin+'/',{waitUntil:'networkidle'});
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,`home overflow at ${width}`);
      if(width===390) await page.screenshot({path:path.join(preview,'mobile.png'),fullPage:true});
      await page.goto(origin+'/app/localsend/',{waitUntil:'networkidle'});
    }
    const offline = await browser.newContext({javaScriptEnabled:false});
    const staticPage = await offline.newPage();
    await staticPage.goto(origin+'/category/office/');
    assert.match(await staticPage.locator('main').innerText(),/LibreOffice/);
    await staticPage.goto(origin+'/app/localsend/');
    assert.match(await staticPage.locator('main').innerText(),/把照片/);
    await offline.close();

    const failed = await context.newPage();
    await failed.route('**/assets/catalog.json',route=>route.abort());
    await failed.goto(origin+'/search/?q=vlc');
    await failed.getByText('搜索目录暂时无法加载').waitFor();
    await failed.close();
    assert.deepEqual(errors,[]);
    console.log('Browser checks passed: search, aliases, filters, empty states, XSS, detail/store links, 5 viewport sizes, no-JS content and network failure.');
  } finally {
    await browser.close();
  }
})().catch(error=>{ console.error(error); process.exitCode=1; });
