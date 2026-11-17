#!/usr/bin/env node
/**
 * wx_clip.mjs — 微信公众号「图片消息/图文」无人值守抓取（浏览器维度，CDP + 真实登录 cookie）
 *
 * 用法:  node wx_clip.mjs <articleUrl> <outDir> [--ocr]
 *   node wx_clip.mjs "https://mp.weixin.qq.com/s/xxxx" ./out --ocr
 *
 * 原理（全部已在本机实测通过）:
 *  1) 风控门 = 数据中心 IP + 无登录态。headless 只要带上真实 profile 的微信 cookie 即放行，
 *     与 headless/UA 指纹无关。复制真实 Chrome 的 Cookies + Local State 到临时 profile，
 *     同一 macOS 用户共享 keychain 的 "Chrome Safe Storage" 密钥，Chrome 可自行解密，无需导明文。
 *  2) headless=new 开 --remote-debugging-port，走 CDP（WebSocket）Page.navigate + Runtime.evaluate。
 *  3) 滚动触发懒加载；图片不能只查 #js_content —— 图片消息的正文在 .share_media 轮播组件里，
 *     沿 img 父链 class 判定 role(main/tag/avatar)，main 即正文卡片图。
 *  4) 下载必须带 Referer: https://mp.weixin.qq.com/；扩展名按 magic bytes 判定（微信实际多为 webp，
 *     不可信 URL 里的 wx_fmt）。
 *  5) 图片型正文用 macOS Vision 离线中文 OCR 还原全文（--ocr）。
 *
 * 依赖: macOS + Google Chrome + Node>=18（内置 WebSocket/fetch）；OCR 需要 swiftc（Xcode CLT）。
 */
import { spawn, execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, cpSync, writeFileSync, readFileSync, readdirSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';

const [,, URL, OUT, ...flags] = process.argv;
if (!URL || !OUT) { console.error('用法: node wx_clip.mjs <articleUrl> <outDir> [--ocr]'); process.exit(1); }
const DO_OCR = flags.includes('--ocr');
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const REAL_CHROME = join(process.env.HOME, 'Library/Application Support/Google/Chrome');
const sleep = ms => new Promise(r => setTimeout(r, ms));
mkdirSync(join(OUT, 'images'), { recursive: true });

/* ---------- 1. 构建带真实登录 cookie 的临时 profile ---------- */
function ensureCookieProfile() {
  const cached = '/tmp/wx_cdp_profile_path.txt';
  if (existsSync(cached)) {
    const p = readFileSync(cached, 'utf8').trim();
    if (existsSync(join(p, 'Default', 'Cookies'))) return p;            // self-heal
  }
  const dir = join(tmpdir(), 'wx-cdp-' + Math.random().toString(36).slice(2, 8));
  const def = join(dir, 'Default');
  mkdirSync(join(def, 'Network'), { recursive: true });
  cpSync(join(REAL_CHROME, 'Local State'), join(dir, 'Local State'));   // 含加密 key 包装
  for (const f of readdirSync(join(REAL_CHROME, 'Default')).filter(x => /^Cookies/i.test(x))) {
    cpSync(join(REAL_CHROME, 'Default', f), join(def, f));              // 同时放两处，兼容不同 Chrome 版本
    cpSync(join(REAL_CHROME, 'Default', f), join(def, 'Network', f));
  }
  const pref = join(REAL_CHROME, 'Default', 'Preferences');
  if (existsSync(pref)) cpSync(pref, join(def, 'Preferences'));
  writeFileSync(cached, dir);
  return dir;
}

/* ---------- 2. 启动 headless Chrome 并建立 CDP 会话 ---------- */
async function launchCdp(profile) {
  const PORT = 9300 + Math.floor(Math.random() * 500);
  const child = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${profile}`, '--no-first-run', '--no-default-browser-check',
    '--disable-gpu', '--window-size=1280,3200', '--lang=zh-CN', 'about:blank'],
    { stdio: ['ignore', 'pipe', 'pipe'] });
  const get = async p => (await fetch(`http://127.0.0.1:${PORT}${p}`)).json();
  let target;
  for (let i = 0; i < 60; i++) {
    try { const l = await get('/json/list'); target = l.find(t => t.type === 'page'); if (target?.webSocketDebuggerUrl) break; }
    catch { /* 等待 DevTools 端口就绪 */ }
    await sleep(250);
  }
  if (!target) { child.kill('SIGKILL'); throw new Error('CDP target 未就绪'); }
  const ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  let id = 0; const pend = new Map();
  ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m.result ?? m); pend.delete(m.id); } };
  const send = (method, params = {}) => new Promise(r => { const mid = ++id; pend.set(mid, r); ws.send(JSON.stringify({ id: mid, method, params })); });
  return {
    send, port: PORT,
    async eval(expression) {
      const r = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
      if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails).slice(0, 300));
      return r.result.value;
    },
    async close() { try { ws.close(); } catch { /* noop */ } child.kill('SIGTERM'); await sleep(200); try { child.kill('SIGKILL'); } catch { /* noop */ } },
  };
}

/* ---------- 3. 渲染后从 DOM 抽取（含轮播组件图片角色判定） ---------- */
const EXTRACT_JS = `(async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  for (let y = 1; y <= 10; y++) { window.scrollTo(0, y * 900); await sleep(300); }
  window.scrollTo(0, 0); await sleep(500);
  const html = document.documentElement.innerHTML;
  const meta = sel => (document.querySelector(sel)?.content || '').trim();
  const gh = (html.match(/user_name:\\s*'([^']+)'/) || [])[1] || '';
  const nick = (html.match(/nick_name:\\s*'([^']+)'/) || [])[1] || '';
  const ts = (html.match(/var\\s+ct\\s*=\\s*["']?(\\d+)/) || [])[1] || '';
  const main = new Set(), tag = new Set(), avatar = new Set();
  document.querySelectorAll('img').forEach(im => {
    const u = im.getAttribute('data-src') || im.currentSrc || im.src || '';
    if (!u.includes('mmbiz.qpic.cn')) return;
    let el = im, chain = [];
    for (let k = 0; k < 7 && el; k++) { el = el.parentElement; if (el?.className) chain.push(el.className); }
    const c = chain.join(' ');
    if (/avatar|head_img|qrcode|wx_follow|jump_author/.test(c)) avatar.add(u);
    else if (/swiper_function_area|swiper_tag_wrp/.test(c)) tag.add(u);
    else if (/swiper_item_img|swiper_item|share_media|swiper_content/.test(c)) main.add(u);
  });
  return JSON.stringify({
    title: (document.querySelector('#activity-name')?.innerText || document.title || '').trim(),
    shareTitle: meta('meta[property="og:title"]'),
    cover: meta('meta[property="og:image"]'),
    ghId: gh, account: nick, publishTs: ts,
    caption: (document.querySelector('#js_image_desc') || document.querySelector('#js_content'))?.innerText?.trim() || '',
    swiperItems: document.querySelectorAll('.share_media .swiper_item').length,
    mainImages: [...main], tagImages: [...tag], avatarImages: [...avatar],
    hasCaptcha: /wappoc_appmsgcaptcha|环境异常/.test(html),
  });
})()`;

/* ---------- 4. 下载图片（Referer + magic bytes 定扩展名） ---------- */
function download(url, fileBase) {
  const buf = execFileSync('curl', ['-sL', url, '-H', 'Referer: https://mp.weixin.qq.com/',
    '-H', 'User-Agent: Mozilla/5.0 Chrome/124.0 Safari/537.36']);
  const ext = buf.subarray(0, 4).toString('ascii') === 'RIFF' ? 'webp'
    : buf[0] === 0xFF && buf[1] === 0xD8 ? 'jpg'
    : buf[0] === 0x89 && buf[1] === 0x50 ? 'png' : 'img';
  const fn = `${fileBase}.${ext}`;
  writeFileSync(join(OUT, 'images', fn), buf);
  return `images/${fn}`;
}

/* ---------- 5. 可选：Vision 离线中文 OCR ---------- */
function visionOcr(webpPaths) {
  const work = join(tmpdir(), 'wxocr-' + Math.random().toString(36).slice(2, 6));
  mkdirSync(work, { recursive: true });
  const pngs = webpPaths.map((w, i) => { const p = join(work, `IMG_${String(i + 1).padStart(2, '0')}.png`);
    execFileSync('sips', ['-s', 'format', 'png', join(OUT, w), '--out', p]); return p; });
  const swift = join(work, 'ocr.swift');
  writeFileSync(swift, `import Vision; import AppKit
for path in Array(CommandLine.arguments.dropFirst()) {
  guard let img = NSImage(contentsOfFile: path), let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { continue }
  let req = VNRecognizeTextRequest()
  req.recognitionLanguages = ["zh-Hans", "en-US"]; req.recognitionLevel = .accurate; req.usesLanguageCorrection = true
  try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
  print("=== \\((path as NSString).lastPathComponent) ===")
  (req.results ?? []).forEach { if let s = $0.topCandidates(1).first?.string { print(s) } }; print("")
}`);
  const bin = join(work, 'ocr_bin');
  execFileSync('swiftc', ['-O', swift, '-o', bin]);
  const out = execFileSync(bin, pngs, { maxBuffer: 64 * 1024 * 1024 }).toString();
  rmSync(work, { recursive: true, force: true });
  return out;
}

/* ---------- 主流程 ---------- */
const profile = ensureCookieProfile();
console.log('cookie profile:', profile);
const cdp = await launchCdp(profile);
try {
  await cdp.send('Page.enable');
  await cdp.send('Page.navigate', { url: URL });
  await sleep(3500);
  const data = JSON.parse(await cdp.eval(EXTRACT_JS));
  if (data.hasCaptcha) throw new Error('仍命中风控验证页：请重新同步真实 Chrome 的登录 cookie');
  console.log(`captcha=否 轮播item=${data.swiperItems} 正文图=${data.mainImages.length}`);

  const images = data.mainImages.map((u, i) => download(u, `IMG_${String(i + 1).padStart(2, '0')}`));
  let coverRel = '';
  if (data.cover) { try { coverRel = download(data.cover, 'cover_share'); } catch { /* 封面可选 */ } }

  const pub = data.publishTs ? new Date(+data.publishTs * 1000).toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai', hour12: false }) : '';
  const meta = { ...data, mainImages: undefined, tagImages: undefined, avatarImages: undefined,
    images, cover: coverRel, publishTime: pub, sourceUrl: URL };
  writeFileSync(join(OUT, 'meta.json'), JSON.stringify(meta, null, 2));

  let ocrSection = '';
  if (DO_OCR && images.length) {
    writeFileSync(join(OUT, 'ocr_raw.txt'), visionOcr(images));
    ocrSection = `\n> 已生成 ocr_raw.txt（Vision 离线 OCR 原始结果，可据此整理完整文字稿）。\n`;
  }
  const gallery = images.map((f, i) => `![轮播卡片 ${i + 1}](${f})`).join('\n\n');
  const md = `# ${data.shareTitle || data.title}\n\n## 元信息\n\n`
    + `- 公众号：${data.account || '(未取到)'}${data.ghId ? `（${data.ghId}）` : ''}\n`
    + `- 发布时间：${pub || '(未取到)'}\n- 原始链接：${URL}\n- 正文轮播图：${images.length} 张\n${ocrSection}\n`
    + `## 配文摘要\n\n${data.caption}\n\n## 原始轮播卡片\n\n${gallery}\n`;
  writeFileSync(join(OUT, 'article.md'), md);
  console.log('完成 →', join(OUT, 'article.md'), '| 图片', images.length, '张');
} finally {
  await cdp.close();
}
