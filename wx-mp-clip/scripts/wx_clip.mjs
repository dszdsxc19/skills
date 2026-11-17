#!/usr/bin/env node
/** 微信公众号离线导出：真实 Chrome cookie、完整轮播来源、Vision OCR 与包内引用校验。 */
import { spawn, execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, cpSync, writeFileSync, readFileSync, readdirSync, rmSync, mkdtempSync, realpathSync } from 'node:fs';
import { join, resolve, dirname, relative, sep } from 'node:path';
import { tmpdir, homedir } from 'node:os';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));
const sleep = ms => new Promise(r => setTimeout(r, ms));

/** 每次复制当前加密登录态；只清理本次创建的副本，不操作真实 Chrome 或历史临时实例。 */
function ensureCookieProfile() {
  const source = join(homedir(), 'Library/Application Support/Google/Chrome');
  const cookies = ['Default/Network', 'Default'].find(p => existsSync(join(source, p, 'Cookies')));
  if (!cookies) throw new Error('真实 Chrome Default 中未找到 Cookies；无法自动取得已有登录态');
  const profile = mkdtempSync(join(tmpdir(), 'wx-cdp-'));
  try {
    cpSync(join(source, 'Local State'), join(profile, 'Local State'));
    for (const target of ['Default', 'Default/Network']) {
      mkdirSync(join(profile, target), { recursive: true });
      for (const name of readdirSync(join(source, cookies)).filter(f => /^Cookies(?:$|-)/.test(f))) {
        cpSync(join(source, cookies, name), join(profile, target, name));
      }
    }
    const preferences = join(source, 'Default/Preferences');
    if (existsSync(preferences)) cpSync(preferences, join(profile, 'Default/Preferences'));
    return profile;
  } catch (error) { rmSync(profile, { recursive: true, force: true }); throw error; }
}

/** Chrome 自选空闲端口；CDP 请求有超时，失败及正常结束均释放自建浏览器。 */
export async function launchCdp(profile) {
  const child = spawn(CHROME, ['--headless=new', '--remote-debugging-port=0',
    '--remote-debugging-address=127.0.0.1', `--user-data-dir=${profile}`,
    '--no-first-run', '--no-default-browser-check', '--disable-gpu',
    '--window-size=1280,3200', '--lang=zh-CN', 'about:blank'], { stdio: 'ignore' });
  let spawnError, ws;
  child.on('error', error => { spawnError = error; });
  const pending = new Map();
  // SIGKILL 仅作为本进程创建的 Chrome 未及时退出时的兜底。
  const close = async () => {
    ws?.close();
    for (const item of pending.values()) { clearTimeout(item.timer); item.reject(new Error('CDP 已关闭')); }
    pending.clear();
    child.kill('SIGTERM');
    await sleep(200);
    if (child.exitCode === null && child.signalCode === null) child.kill('SIGKILL');
  };
  try {
    let target;
    for (let i = 0; i < 60; i++) {
      if (spawnError) throw spawnError;
      if (child.exitCode !== null) throw new Error('Chrome 提前退出');
      try {
        const port = readFileSync(join(profile, 'DevToolsActivePort'), 'utf8').split('\n')[0];
        const list = await (await fetch(`http://127.0.0.1:${port}/json/list`, { signal: AbortSignal.timeout(1000) })).json();
        target = list.find(t => t.type === 'page' && t.webSocketDebuggerUrl);
        if (target) break;
      } catch { /* 等待本实例写出 DevToolsActivePort。 */ }
      await sleep(250);
    }
    if (!target) throw new Error('CDP target 未就绪');
    ws = new WebSocket(target.webSocketDebuggerUrl);
    await new Promise((res, rej) => {
      const timer = setTimeout(() => rej(new Error('CDP 连接超时')), 10000);
      ws.onopen = () => { clearTimeout(timer); res(); };
      ws.onerror = () => { clearTimeout(timer); rej(new Error('CDP 连接失败')); };
    });
    let id = 0;
    ws.onmessage = event => {
      const message = JSON.parse(event.data), item = pending.get(message.id);
      if (!item) return;
      clearTimeout(item.timer); pending.delete(message.id);
      if (message.error) item.reject(new Error(message.error.message)); else item.resolve(message.result);
    };
    const send = (method, params = {}) => new Promise((res, rej) => {
      const mid = ++id;
      const timer = setTimeout(() => { pending.delete(mid); rej(new Error(`CDP 超时：${method}`)); }, 30000);
      pending.set(mid, { resolve: res, reject: rej, timer });
      ws.send(JSON.stringify({ id: mid, method, params }));
    });
    return { send, close, async eval(expression) {
      const result = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
      if (result.exceptionDetails) throw new Error('页面抽取脚本执行失败');
      return result.result.value;
    } };
  } catch (error) { await close(); throw error; }
}

/** 在真实 DOM 中执行；轮播 item 的 data-src 在 img 尚未创建时也完整存在。 */
export function extractArticle() {
  const html = document.documentElement.innerHTML;
  const meta = selector => (document.querySelector(selector)?.content || '').trim();
  const field = name => (html.match(new RegExp(`\\b${name}\\s*:\\s*['\"]([^'\"]+)['\"]`)) || [])[1] || '';
  // 格式参数只改变同一资源的表示；保留其余查询参数，避免合并不同内容。
  const imageKey = value => {
    try {
      const url = new URL(value, location.href);
      if (!/^https?:$/.test(url.protocol)) return '';
      for (const key of ['wx_fmt', 'from', 'wxfrom', 'tp', 'usePicPrefetch', 'watermark']) url.searchParams.delete(key);
      url.searchParams.sort(); url.hash = '';
      return url.href;
    } catch { return ''; }
  };
  const isAsset = value => { try { return /(^|\.)mmbiz\.qpic\.cn$/.test(new URL(value, location.href).hostname); } catch { return false; } };
  const items = [...document.querySelectorAll('.share_media .swiper_item')]
    .filter(el => !el.closest('.swiper_function_area,.swiper_tag_wrp'));
  const canonical = items.filter(el => isAsset(el.getAttribute('data-src')));
  const images = [], seen = new Set();
  // 正式轮播存在时丢弃占位容器及其带水印的重复首图；不依赖图片像素相似度猜测去重。
  const candidates = canonical.length ? canonical.map(el => el.getAttribute('data-src'))
    : [...document.querySelectorAll('.share_media .swiper_item img, #js_content img')]
      .filter(el => !el.closest('.swiper_function_area,.swiper_tag_wrp,.avatar,.qrcode') && el.id !== 'img_item_placeholder')
      .map(el => el.getAttribute('data-src') || el.currentSrc || el.src);
  for (const value of candidates) {
    const key = imageKey(value);
    if (isAsset(value) && key && !seen.has(key)) { seen.add(key); images.push(new URL(value, location.href).href); }
  }
  const timestampCandidates = [
    ['window.ct', window.ct],
    ['script.ct', (html.match(/\b(?:window\.)?ct\s*=\s*['"]?(\d{10,})/) || [])[1]],
    ['script.create_time', (html.match(/\b(?:ori_create_time|create_timestamp)\s*:\s*['"]?(\d{10,})/) || [])[1]],
  ];
  const timestamp = timestampCandidates.find(([, value]) => /^\d{10,}$/.test(String(value || '')));
  const pageTitle = (document.querySelector('#activity-name')?.innerText || document.title || '').trim();
  return {
    title: pageTitle, pageTitle, shareTitle: meta('meta[property="og:title"]'), titleSource: 'page',
    coverUrl: meta('meta[property="og:image"]'), ghId: field('user_name'), account: field('nick_name'),
    publishTs: timestamp ? Number(timestamp[1]) : null, publishTsSource: timestamp?.[0] || '',
    caption: (document.querySelector('#js_image_desc') || document.querySelector('#js_content'))?.innerText?.trim() || '',
    bodyInImages: items.length > 0, mainImages: images, swiperItems: images.length,
    extraction: { domSwiperItems: items.length, canonicalItems: canonical.length,
      placeholderItems: items.filter(el => el.querySelector('#img_item_placeholder')).length,
      duplicateUrls: candidates.length - images.length },
    hasCaptcha: /wappoc_appmsgcaptcha|环境异常/.test(document.body?.innerText || '')
      || /(?:^|\/)wappoc_appmsgcaptcha(?:\/|$)/.test(location.pathname),
  };
}

/** 等待文章组件稳定；0 图再等待一次，而不是把摘要页误报为完整图片消息。 */
async function readArticle(url) {
  let captchaEncountered = false;
  for (let attempt = 0; attempt < 2; attempt++) {
    const profile = ensureCookieProfile();
    let cdp;
    try {
      cdp = await launchCdp(profile);
      await cdp.send('Page.enable');
      const navigation = await cdp.send('Page.navigate', { url });
      if (navigation.errorText) throw new Error(`文章导航失败：${navigation.errorText}`);
      let data, previous = '', stable = 0;
      for (let poll = 0; poll < 25; poll++) {
        await sleep(400);
        data = await cdp.eval(`(${extractArticle.toString()})()`);
        if (data.hasCaptcha) break;
        const signature = JSON.stringify([data.mainImages, data.publishTs, data.ghId]);
        stable = signature === previous ? stable + 1 : 0; previous = signature;
        if (data.ghId && (data.mainImages.length || data.caption) && stable >= 3 && poll >= 7) break;
      }
      if (data.hasCaptcha) {
        captchaEncountered = true;
        if (attempt === 0) { console.warn('命中风控，重新复制当前真实 Chrome 登录态后重试一次'); continue; }
        throw new Error('刷新真实 Chrome cookie 后仍命中风控；已停止，未要求人工验证码');
      }
      if (data.bodyInImages && !data.mainImages.length) throw new Error('图片消息的轮播来源为空，未产出成功结果');
      if (!data.ghId || !data.title) throw new Error('未取得文章身份，可能是失效链接或尚未就绪的页面');
      return { ...data, captchaEncountered };
    } finally {
      await cdp?.close();
      rmSync(profile, { recursive: true, force: true });
    }
  }
}

/** 文件后缀由完整签名决定；HTTP 错误页与未知格式不能伪装成成功图片。 */
export function detectImageFormat(buf) {
  if (buf.subarray(0, 4).toString('ascii') === 'RIFF' && buf.subarray(8, 12).toString('ascii') === 'WEBP') return 'webp';
  if (buf[0] === 0xFF && buf[1] === 0xD8 && buf[2] === 0xFF) return 'jpg';
  if (buf.subarray(0, 8).equals(Buffer.from([0x89, 0x50, 0x4e, 0x47, 13, 10, 26, 10]))) return 'png';
  throw new Error('图片 magic bytes 不属于 WebP/JPEG/PNG');
}

/** curl 保留 Referer，网络/格式错误最多重试一次；文件校验后才写入图片清单。 */
function download(url, base, out) {
  const work = mkdtempSync(join(tmpdir(), 'wx-download-'));
  try {
    let error;
    for (let attempt = 0; attempt < 2; attempt++) {
      try {
        const dest = join(work, 'image');
        const status = execFileSync('curl', ['--silent', '--show-error', '--location', '--fail', '--max-time', '45',
          url, '-H', 'Referer: https://mp.weixin.qq.com/', '-H', 'User-Agent: Mozilla/5.0 Chrome/124.0 Safari/537.36',
          '--output', dest, '--write-out', '%{http_code}'], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
        if (status.trim() !== '200') throw new Error(`HTTP ${status.trim()}`);
        const buf = readFileSync(dest), format = detectImageFormat(buf);
        const dimensions = execFileSync('sips', ['-g', 'pixelWidth', '-g', 'pixelHeight', dest], { encoding: 'utf8' });
        const width = Number(dimensions.match(/pixelWidth:\s*(\d+)/)?.[1]);
        const height = Number(dimensions.match(/pixelHeight:\s*(\d+)/)?.[1]);
        if (!width || !height) throw new Error('无法解码图片尺寸');
        const path = `images/${base}.${format}`;
        writeFileSync(join(out, path), buf);
        return { path, sourceUrl: url, httpStatus: 200, format, width, height, bytes: buf.length,
          sha256: createHash('sha256').update(buf).digest('hex') };
      } catch (caught) { error = caught; }
    }
    throw new Error(`${base} 下载或格式验证失败：${error.message}`);
  } finally { rmSync(work, { recursive: true, force: true }); }
}

/** 合并卡片硬换行；中英文边界补空格，英文连字符后的断行直接续接。 */
function joinText(left, right) {
  if (!left) return right.trim();
  const space = /[\p{L}\p{N}]$/u.test(left) && /^[A-Za-z0-9]/.test(right)
    || /[A-Za-z0-9]$/.test(left) && /^[\p{L}\p{N}]/u.test(right);
  return left + (space ? ' ' : '') + right.trim();
}

/** 用版面位置和字号恢复标题/段落；保留 OCR 底稿，不按这篇文章的固定词句拼全文。 */
export function formatOcrPages(pages, account = '') {
  const median = values => { const sorted = [...values].sort((a, b) => a - b); return sorted[Math.floor(sorted.length / 2)] || 0; };
  const chapters = [], blocks = [], cardDates = new Set(), emptyImages = [];
  let title = '', handle = '', previousHeading = '';
  for (const page of pages) {
    if (!page.lines.length) { emptyImages.push(page.file); continue; }
    // 已识别出的账号/署名确定页眉区域，同时过滤头像徽章产生的孤立 OCR 碎片。
    const headerLines = page.lines.filter(line => line.y > 0.84
      && (/^[@＠◎]/.test(line.text) || account && line.text.startsWith(account) && line.text.length <= account.length + 2));
    const headerFloor = headerLines.length ? Math.min(...headerLines.map(line => line.y)) - 0.015 : 1;
    const lines = page.lines.filter(line => {
      const text = line.text.trim();
      if (line.y > 0.84 && /^\d{4}[/-]\d{1,2}[/-]\d{1,2}$/.test(text)) { cardDates.add(text.replaceAll('/', '-')); return false; }
      if (line.y > 0.84 && /^[@＠◎]/.test(text)) { handle ||= text.replace(/^[＠◎]/, '@'); return false; }
      if (line.y > 0.84 && account && text.startsWith(account) && text.length <= account.length + 2) return false;
      if (line.y >= headerFloor) return false;
      if (line.y < 0.08 && /多搜索.*多动手|Vibe\s*Any|公众号[·•：:]/i.test(text)) return false;
      return Boolean(text);
    }).sort((a, b) => (b.y + b.height) - (a.y + a.height));
    if (!lines.length) { emptyImages.push(page.file); continue; }
    // 同一水平行可能由多段着色文字或表格单元格组成，先按垂直重叠合并。
    const rows = [];
    for (const line of lines) {
      const row = rows.find(r => Math.min(r.y + r.height, line.y + line.height) - Math.max(r.y, line.y) > Math.min(r.height, line.height) * 0.5);
      if (row) { row.parts.push(line); row.height = Math.max(row.height, line.height); }
      else rows.push({ ...line, parts: [line] });
    }
    for (const row of rows) {
      const parts = row.parts.sort((a, b) => a.x - b.x);
      row.text = parts.reduce((s, part, i) => {
        const previous = parts[i - 1];
        const separateCell = previous && part.x - previous.x - previous.width > row.height * 2.5;
        row.tableRow ||= Boolean(separateCell);
        return separateCell ? s + ' | ' + part.text.trim() : joinText(s, part.text);
      }, '');
    }
    const bodyHeight = median(rows.map(r => r.height));
    let heading = '';
    if (!title && !blocks.length) {
      while (rows.length && rows[0].height > bodyHeight * 1.45) heading = joinText(heading, rows.shift().text);
    } else if (rows[0]?.height > bodyHeight * 1.10) {
      // 正文章节只取首行，避免把紧邻且字号接近的第一句吞进标题。
      heading = rows.shift().text;
    }
    if (heading) {
      if (!title && !blocks.length) title = heading;
      else if (heading !== previousHeading) { chapters.push(heading); blocks.push(`## ${heading}`); previousHeading = heading; }
    }
    const gaps = rows.slice(1).map((row, i) => Math.max(0, rows[i].y - row.y - row.height));
    const paragraphGap = Math.max(median(gaps) * 1.6, bodyHeight * 0.7);
    let paragraph = '';
    for (let i = 0; i < rows.length; i++) {
      const row = rows[i], previous = rows[i - 1];
      const gap = previous ? previous.y - row.y - row.height : 0;
      const shortSentence = previous && /[。！？：]$/.test(previous.text) && previous.width < 0.75;
      if (paragraph && (gap > paragraphGap || shortSentence || row.tableRow || previous?.tableRow
        || /^\d+[.、]\s*/.test(row.text))) { blocks.push(paragraph); paragraph = ''; }
      paragraph = joinText(paragraph, row.text);
    }
    if (paragraph) blocks.push(paragraph);
  }
  return { title, chapters, body: blocks.join('\n\n'), cardDates: [...cardDates], handle, emptyImages };
}

/** 一次编译批量识别；空结果或识别错误仅对受影响图片用关闭语言校正的模式重试一次。 */
function visionOcr(images, out, account) {
  const work = mkdtempSync(join(tmpdir(), 'wxocr-'));
  try {
    const pngs = images.map((image, i) => {
      const path = join(work, `IMG_${String(i + 1).padStart(2, '0')}.png`);
      execFileSync('sips', ['-s', 'format', 'png', join(out, image), '--out', path], { stdio: 'pipe' });
      return path;
    });
    const bin = join(work, 'ocr');
    execFileSync('swiftc', ['-O', join(SCRIPT_DIR, 'vision_ocr.swift'), '-o', bin], { stdio: 'pipe' });
    const recognize = args => JSON.parse(execFileSync(bin, args, { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024, stdio: 'pipe' }));
    const pages = recognize(pngs);
    const retryIndexes = pages.flatMap((p, i) => p.error || !p.lines.length ? [i] : []);
    if (retryIndexes.length) {
      const retried = recognize(['--no-correction', ...retryIndexes.map(i => pngs[i])]);
      retryIndexes.forEach((index, i) => { pages[index] = retried[i]; });
    }
    writeFileSync(join(out, 'ocr_layout.json'), JSON.stringify(pages, null, 2) + '\n');
    writeFileSync(join(out, 'ocr_raw.txt'), pages.map(p => `=== ${p.file} ===\n${p.lines.map(l => l.text).join('\n')}\n`).join('\n'));
    if (pages.length !== images.length || pages.some(p => p.error)) throw new Error('部分图片 OCR 失败，已保留识别底稿');
    const formatted = formatOcrPages(pages, account);
    if (!formatted.body.trim()) throw new Error('OCR 重试后全文仍为空，已保留图片及底稿');
    return { ...formatted, imageCount: pages.length, retryImageCount: retryIndexes.length };
  } finally { rmSync(work, { recursive: true, force: true }); }
}

/** 仅检查真实文件与数据一致性；不把固定图片数、字数、章节数当成功门槛。 */
export function verifyOutput(out, meta, expectOcr) {
  const files = ['article.md', 'meta.json', ...(expectOcr ? ['article_fulltext.md', 'ocr_raw.txt', 'ocr_layout.json'] : [])];
  for (const path of files) if (!existsSync(join(out, path))) throw new Error(`缺失产物：${path}`);
  const imageDetails = [...meta.imageDetails, ...(meta.coverDetails ? [meta.coverDetails] : [])];
  for (const image of imageDetails) {
    const buf = readFileSync(join(out, image.path));
    if (!image.path.endsWith('.' + detectImageFormat(buf))) throw new Error(`图片扩展名不匹配：${image.path}`);
  }
  let imageReferences = 0;
  for (const file of files.filter(p => p.endsWith('.md'))) {
    const text = readFileSync(join(out, file), 'utf8');
    for (const match of text.matchAll(/(!?)\[[^\]]*\]\(([^)]+)\)/g)) {
      const link = match[2], local = resolve(out, link), rel = relative(resolve(out), local);
      if (/^(?:[a-z]+:|\/\/)/i.test(link) || rel === '..' || rel.startsWith('..' + sep) || !existsSync(local)) throw new Error(`包外或缺失引用：${link}`);
      if (match[1]) imageReferences++;
    }
  }
  if (meta.images.length !== meta.swiperItems) throw new Error('下载正文图数与抽取清单不一致');
  if (expectOcr) {
    const sections = [...readFileSync(join(out, 'ocr_raw.txt'), 'utf8').matchAll(/^=== IMG_\d+\.png ===$/gm)];
    if (sections.length !== meta.images.length) throw new Error('OCR 分节数与正文图数不一致');
  }
  return { requiredFilesPresent: true, bodyImageCount: meta.images.length, totalImageCount: imageDetails.length,
    imageReferences, missingReferences: [], externalReferences: [], images: imageDetails.map(({ sourceUrl, ...image }) => image) };
}

/** 输出来源保存在元数据；正文和画廊只使用包内链接，便于离线移动。 */
export async function run(url, output, doOcr = false) {
  const started = Date.now(), out = resolve(output);
  if (new URL(url).hostname !== 'mp.weixin.qq.com') throw new Error('输入必须是 mp.weixin.qq.com 文章 URL');
  mkdirSync(join(out, 'images'), { recursive: true });
  const oldMeta = existsSync(join(out, 'meta.json')) ? JSON.parse(readFileSync(join(out, 'meta.json'), 'utf8')) : null;
  const warnings = [];
  const meta = { sourceUrl: url, status: 'processing', warnings, images: [], imageDetails: [], cover: '', coverDetails: null };
  const saveMeta = () => writeFileSync(join(out, 'meta.json'), JSON.stringify(meta, null, 2) + '\n');
  // 新一轮开始即撤下旧的成功报告，导航、下载失败也必须写入本轮失败状态。
  if (oldMeta) rmSync(join(out, 'verification.json'), { force: true });
  saveMeta();
  try {
    const data = await readArticle(url);
    const { mainImages, coverUrl, ...fields } = data;
    const publishTime = data.publishTs ? new Intl.DateTimeFormat('sv-SE', { timeZone: 'Asia/Shanghai',
      year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23' })
      .format(new Date(data.publishTs * 1000)).replace(',', '') + '+08:00' : '';
    Object.assign(meta, fields, { publishTime });
    saveMeta();
    const imageDetails = meta.imageDetails;
    for (const [i, src] of data.mainImages.entries()) {
      const image = download(src, `IMG_${String(i + 1).padStart(2, '0')}`, out);
      imageDetails.push(image); meta.images.push(image.path); saveMeta();
    }
    if (data.coverUrl) {
      try { meta.coverDetails = download(data.coverUrl, 'cover_share', out); meta.cover = meta.coverDetails.path; }
      catch (error) { warnings.push(error.message); }
    }
    saveMeta();
    let body = data.caption, ocr = null;
    if (doOcr) {
      if (!imageDetails.length) throw new Error('--ocr 未找到可识别的正文图片');
      ocr = visionOcr(meta.images, out, data.account);
      body = ocr.body;
      if (data.bodyInImages && ocr.title) { meta.title = ocr.title; meta.titleSource = 'OCR: ' + meta.images[0]; }
      const plain = body.replace(/^#{1,6}\s+/gm, '').replace(/^\d+[.、]\s*/gm, '').replace(/\s/g, '');
      meta.ocr = { engine: 'macOS Vision', imageCount: ocr.imageCount, retryImageCount: ocr.retryImageCount,
        emptyImages: ocr.emptyImages, chapterTitles: ocr.chapters, chapterCount: ocr.chapters.length,
        nonWhitespaceCharacters: plain.length, hanCharacters: (plain.match(/[\u3400-\u4dbf\u4e00-\u9fff]/g) || []).length,
        cardDates: ocr.cardDates, handle: ocr.handle };
      if (ocr.emptyImages.length) warnings.push(`这些图片未识别到文字：${ocr.emptyImages.join(', ')}`);
      const source = `出处：${data.account}（${data.ghId}）${ocr.handle ? '；' + ocr.handle : ''}；发布时间 ${publishTime || '未取到'}。`
        + `${ocr.cardDates.length ? '卡片日期：' + ocr.cardDates.join('、') + '。' : ''}来源地址见 [meta.json](meta.json)。`;
      writeFileSync(join(out, 'article_fulltext.md'), `# ${meta.title}\n\n> 本文由原始图片经 macOS Vision 离线 OCR 自动整理；保留识别误差的可能。原始结果见 [ocr_raw.txt](ocr_raw.txt)，原图见 [article.md](article.md)。\n\n${body}\n\n---\n\n${source}\n`);
    }
    if (!publishTime) warnings.push('未取得发布时间；未使用卡片日期替代');
    const gallery = meta.images.map((p, i) => `![轮播卡片 ${i + 1}](${p})`).join('\n\n');
    const info = `- 公众号：${data.account}（${data.ghId}）\n- 发布时间：${publishTime || '未取到'}\n- 页面分享标题：${data.shareTitle || data.pageTitle}\n- 正文图片：${meta.images.length} 张\n- 来源及图片清单：[meta.json](meta.json)\n`;
    writeFileSync(join(out, 'article.md'), `# ${meta.title}\n\n${info}\n${ocr ? '> 正文由图片离线 OCR 自动整理；另见 [article_fulltext.md](article_fulltext.md)。\n\n' : ''}${body}\n\n## 原始图片\n\n${gallery}\n${meta.cover ? '\n## 分享封面\n\n![分享封面](' + meta.cover + ')\n' : ''}${data.bodyInImages ? '\n## DOM 配文摘要\n\n' + data.caption + '\n' : ''}`);
    saveMeta();
    const verification = verifyOutput(out, meta, doOcr);
    meta.status = 'completed'; saveMeta();
    // 重跑仅清除上一份清单明确拥有、这次已替换的生成文件，保留用户自有文件。
    const current = new Set([...meta.images, meta.cover, ...(doOcr ? ['article_fulltext.md', 'ocr_raw.txt', 'ocr_layout.json'] : [])]);
    const previous = [...(oldMeta?.images || []), oldMeta?.cover,
      ...(oldMeta?.ocr ? ['article_fulltext.md', 'ocr_raw.txt', 'ocr_layout.json'] : [])].filter(Boolean);
    for (const path of previous) if (/^(?:images\/(?:IMG_\d+|cover_share)\.(?:png|jpg|webp)|article_fulltext\.md|ocr_raw\.txt|ocr_layout\.json)$/.test(path) && !current.has(path)) rmSync(join(out, path), { force: true });
    writeFileSync(join(out, 'verification.json'), JSON.stringify({ ...verification, exitCode: 0, ocr: meta.ocr,
      captchaEncountered: data.captchaEncountered, totalElapsedSeconds: (Date.now() - started) / 1000, warnings }, null, 2) + '\n');
    console.log(`完成：${join(out, 'article.md')} | 正文图 ${meta.images.length} 张 | OCR 章节 ${meta.ocr?.chapterCount ?? '未启用'}`);
    return meta;
  } catch (error) { meta.status = 'failed'; meta.error = error.message; saveMeta(); throw error; }
}

// 导入测试不启动浏览器；CLI 错误明确返回非零状态，不把部分产物当作成功。
if (process.argv[1] && existsSync(process.argv[1])
  && import.meta.url === pathToFileURL(realpathSync(process.argv[1])).href) {
  const [url, out, ...flags] = process.argv.slice(2);
  if (!url || !out || flags.some(flag => flag !== '--ocr')) {
    console.error('用法：node wx_clip.mjs <articleUrl> <outDir> [--ocr]'); process.exitCode = 1;
  } else {
    try { await run(url, out, flags.includes('--ocr')); }
    catch (error) { console.error(`导出失败：${error.message}`); process.exitCode = 1; }
  }
}
