import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, rmSync, writeFileSync, mkdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { launchCdp, extractArticle, detectImageFormat, formatOcrPages, verifyOutput } from './wx_clip.mjs';

let cdp, profile, fixtureId = 0;
before(async () => {
  profile = mkdtempSync(join(tmpdir(), 'wx-clip-test-'));
  cdp = await launchCdp(profile);
});
after(async () => {
  await cdp?.close();
  if (profile) rmSync(profile, { recursive: true, force: true });
});

/** 真实 Chrome 渲染本地 HTML，覆盖节点缺失的轮播状态，不依赖手写 DOM mock。 */
async function extractFixture(body, script = "window.ct = '1794752814';") {
  const title = `页面标题${++fixtureId}`;
  const html = `<title>${title}</title><script>${script}
    const account = {user_name: 'gh_fixture', nick_name: '测试号'};</script>${body}`;
  await cdp.send('Page.navigate', { url: 'data:text/html;charset=utf-8,' + encodeURIComponent(html) });
  // document.title 来自本轮 fixture，避免读取到上一轮导航文档。
  for (let i = 0; i < 100; i++) {
    if (await cdp.eval(`document.readyState === "complete" && document.title === ${JSON.stringify(title)}`)) break;
    await new Promise(r => setTimeout(r, 10));
  }
  return cdp.eval(`(${extractArticle.toString()})()`);
}

test('完整读取没有 img 的懒加载条目，排除占位首图和功能区', async () => {
  const data = await extractFixture(`
    <div class="share_media"><div class="swiper_item"><img id="img_item_placeholder" data-src="https://mmbiz.qpic.cn/a/0?tp=webp"></div></div>
    <div class="share_media">
      <div class="swiper_item" data-src="https://mmbiz.qpic.cn/a/0?wx_fmt=png"></div>
      <div class="swiper_item" data-src="https://mmbiz.qpic.cn/b/0?wx_fmt=png"></div>
      <div class="swiper_item" data-src="https://mmbiz.qpic.cn/c/0?wx_fmt=png"></div>
      <div class="swiper_function_area"><div class="swiper_item" data-src="https://mmbiz.qpic.cn/tag/0"></div></div>
    </div>`);
  assert.equal(data.mainImages.length, 3);
  assert.equal(data.swiperItems, 3);
  assert.equal(data.extraction.domSwiperItems, 4);
  assert.equal(data.extraction.placeholderItems, 1);
  assert.equal(data.publishTs, 1794752814);
  assert.equal(data.publishTsSource, 'window.ct');
  assert.equal(data.bodyInImages, true);
});

test('同一资源的格式参数去重，其他查询参数代表的内容保留', async () => {
  const data = await extractFixture(`<div class="share_media">
    <div class="swiper_item" data-src="https://mmbiz.qpic.cn/a/0?id=1&tp=webp"></div>
    <div class="swiper_item" data-src="https://mmbiz.qpic.cn/a/0?id=1&wx_fmt=png"></div>
    <div class="swiper_item" data-src="https://mmbiz.qpic.cn/a/0?id=2"></div>
  </div>`, "const ct = '1794752814';");
  assert.equal(data.mainImages.length, 2);
  assert.equal(data.publishTs, 1794752814);
  assert.equal(data.publishTsSource, 'script.ct');
});

test('普通图文仍保留正文图，发布时间缺失时不伪造', async () => {
  const data = await extractFixture('<div id="js_content">正文<img data-src="https://mmbiz.qpic.cn/a/0"></div>', '');
  assert.equal(data.mainImages.length, 1);
  assert.equal(data.bodyInImages, false);
  assert.equal(data.publishTs, null);
  assert.equal(data.caption, '正文');
});

test('根据真实页面文本识别风控，脚本里的同名字符串不造成误报', async () => {
  assert.equal((await extractFixture('<p>环境异常，完成验证后即可继续访问</p>')).hasCaptcha, true);
  assert.equal((await extractFixture('<p>正文</p>', "const marker = 'wappoc_appmsgcaptcha';")).hasCaptcha, false);
});

test('magic bytes 决定后缀，拒绝 HTML 和伪 RIFF', () => {
  assert.equal(detectImageFormat(Buffer.from('RIFF0000WEBPdata')), 'webp');
  assert.equal(detectImageFormat(Buffer.from([255, 216, 255, 224])), 'jpg');
  assert.equal(detectImageFormat(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10])), 'png');
  assert.throws(() => detectImageFormat(Buffer.from('<html>error</html>')));
  assert.throws(() => detectImageFormat(Buffer.from('RIFF0000WAVEdata')));
});

/** 用位置和字号构造另一篇文章，验证全文整理不依赖回归样本的标题或章节名称。 */
test('自动生成完整正文、合并多行标题、去页眉页脚及续页重复标题', () => {
  const line = (text, y, height = 0.025) => ({ text, x: 0.05, y, height, width: 0.9 });
  const formatted = formatOcrPages([
    { file: 'IMG_01.png', lines: [
      line('测试号', 0.95), line('@实验室', 0.90), line('2026/11/14', 0.90),
      line('徽章噪声', 0.945, 0.02),
      line('理解模型', 0.76, 0.08), line('benchmark 的方法', 0.65, 0.08),
      line('这是介绍的第一行，', 0.50), line('继续介绍。', 0.46),
      line('另一段。', 0.36), line('Vibe Anything', 0.02),
    ] },
    { file: 'IMG_02.png', lines: [
      line('观察与验证', 0.82, 0.0285), line('第一部分正文。', 0.73, 0.0277), line('第二句。', 0.67),
      line('第三句。', 0.60), line('第四句。', 0.54),
    ] },
    { file: 'IMG_03.png', lines: [
      line('观察与验证', 0.82, 0.0285), line('续页正文。', 0.73), line('最后一句。', 0.67),
    ] },
  ], '测试号');
  assert.equal(formatted.title, '理解模型 benchmark 的方法');
  assert.deepEqual(formatted.chapters, ['观察与验证']);
  assert.match(formatted.body, /这是介绍的第一行，继续介绍。/);
  assert.match(formatted.body, /续页正文。/);
  assert.doesNotMatch(formatted.body, /测试号|实验室|徽章噪声|Vibe Anything/);
  assert.equal(formatted.cardDates[0], '2026-11-14');
});

test('自包含校验拒绝丢失和外部图片，不能仅因 Markdown 文件存在就成功', () => {
  const out = mkdtempSync(join(tmpdir(), 'wx-verify-test-'));
  const meta = { images: [], imageDetails: [], swiperItems: 0 };
  try {
    mkdirSync(join(out, 'images'));
    writeFileSync(join(out, 'meta.json'), '{}');
    writeFileSync(join(out, 'article.md'), '![缺失](images/missing.png)');
    assert.throws(() => verifyOutput(out, meta, false), /缺失引用/);
    writeFileSync(join(out, 'article.md'), '![远程](https://example.com/image.png)');
    assert.throws(() => verifyOutput(out, meta, false), /包外/);
    writeFileSync(join(out, 'article.md'), '[元信息](meta.json)');
    assert.equal(verifyOutput(out, meta, false).requiredFilesPresent, true);
  } finally { rmSync(out, { recursive: true, force: true }); }
});
