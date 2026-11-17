---
name: wx-mp-clip
description: Use when the user wants to autonomously fetch, clip, export, or archive a WeChat public-account article (mp.weixin.qq.com), especially "image message" / carousel posts whose real body lives in swipeable card images rather than the DOM. Drives headless Chrome over CDP with a copy of the real Chrome profile's WeChat login cookies to pass the server-side wappoc_appmsgcaptcha anti-bot gate, downloads carousel/cover images with the correct Referer, and restores full text via offline macOS Vision OCR, emitting self-contained Markdown. Triggers on 微信公众号/公众号文章/图文/图片消息/轮播图/剪藏/导出/风控验证/环境异常/cookie 抓取, or any mp.weixin.qq.com/s/ URL that must be saved without manual copy-paste or print-to-PDF.
---

# 微信公众号无人值守抓取（CDP + 真实 cookie + 轮播图 + Vision OCR）

把一篇 `mp.weixin.qq.com/s/...` 文章，**无人工**抓成自包含 Markdown（正文 + 原图 + 元数据）。对微信「图片消息」（正文印在轮播卡片图里、DOM 只有配文摘要）也能还原全文。

## 何时用

- 用户给微信公众号文章链接，要自动导出/剪藏/存档，明确不要手动 PDF、打印、复制粘贴。
- 命中微信风控页 `wappoc_appmsgcaptcha`（"环境异常，完成验证后即可继续访问"），需要无人值守通过。
- 文章是图文/图片消息，正文在轮播图里，普通 DOM 抽取得到的文字明显过短、图片为 0。
- 需要把正文图片真正下载到本地，并对图片型正文做 OCR 出文字稿。

## 前置依赖（macOS）

- Google Chrome（默认路径 `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`）。
- Node ≥ 18（内置全局 `WebSocket`/`fetch`，无需 puppeteer）。
- 本机真实 Chrome 里**已登录过微信网页/公众号**（`~/Library/Application Support/Google/Chrome/Default/Cookies*` 含 `poc_sid`/`wr_skey`/`wxtokenkey`/`wxuin` 等会话 cookie）。
- 可选 OCR：`swiftc` + `sips`（Xcode Command Line Tools），用于离线中文识别。

## 快速用法

```bash
# 基本：抓取 + 下图，出 article.md / meta.json / images/
node scripts/wx_clip.mjs "https://mp.weixin.qq.com/s/<TOKEN>" ./out

# 加 --ocr：额外用 macOS Vision 对正文卡片图离线 OCR，出 ocr_raw.txt
node scripts/wx_clip.mjs "https://mp.weixin.qq.com/s/<TOKEN>" ./out --ocr
```

脚本自带临时 cookie profile 构建与自愈、CDP 会话、滚动懒加载、轮播图角色判定、Referer 下载、magic-bytes 定扩展名、可选 OCR。`node --check scripts/wx_clip.mjs` 可做静态校验。

## 核心原理（5 步，全部本机实测）

1. **风控门 = 登录态，不是无头指纹。** 微信拦的是「数据中心出口 IP + 无会话 cookie」；headless 标志、UA、`navigator.webdriver` 都不是决定因素。把真实 Chrome 的 `Default/Cookies*` + `Local State` + `Preferences` 复制到一个临时 `--user-data-dir` 即可——同一 macOS 用户共享 keychain 的 "Chrome Safe Storage" 密钥，Chrome 启动时自行解密 cookie，**无需导出明文、不触碰正在运行的 Chrome**。无 cookie 对照必被重定向到验证页。
2. **CDP 驱动 headless Chrome。** `--headless=new --remote-debugging-port=PORT --user-data-dir=<临时profile>`，轮询 `http://127.0.0.1:PORT/json/list` 取 `webSocketDebuggerUrl`，连 WebSocket 后发 `Page.enable` / `Page.navigate` / `Runtime.evaluate`。
3. **渲染后抽取，先滚动。** 逐段 `window.scrollTo` 触发 `data-src` 懒加载再取 DOM。**图片不能只查 `#js_content`**：图片消息的正文图在独立的 `.share_media → .swiper_item → .swiper_item_img` 轮播组件里。对每张 mmbiz `img` 沿父链 class 判角色——`main`（正文卡片）/ `tag`（功能区标签）/ `avatar`（头像二维码，跳过）。
4. **下载两个硬细节。** ① 必须带 `Referer: https://mp.weixin.qq.com/`，否则 CDN 拒；② 扩展名按 **magic bytes** 判定，微信常回 WebP 而 URL 的 `wx_fmt=png` 会误导（RIFF→webp / FFD8→jpg / 8950→png）。
5. **图片型正文补 OCR。** `sips -s format png` 转码，`swiftc` 编译 Vision 的 `VNRecognizeTextRequest`（`zh-Hans` accurate、`usesLanguageCorrection`）离线识别，再去页眉页脚、并自然段、校噪声，整理成完整文字稿。

## 关键约束与易错点（详见 references/troubleshooting.md）

- **风控命中要 fail loud**：抽取结果含 `wappoc_appmsgcaptcha|环境异常` 时直接报错并提示重建 cookie，不要产出残缺文章。
- **图片消息的 DOM 配文只是摘要**：`#js_image_desc` 文本短不代表正文短；以轮播 main 图数量 + OCR 为准。
- **静态正则不可靠**：合集/轮播页类名同时出现在 `<style>` 与 DOM，固定字符窗口会误判容器；以活浏览器 DOM 的父链判定为权威。
- **shell 循环丢最后一行**：`while read` 遇无结尾换行的清单会漏掉末张图，用 `|| [ -n "$line" ]` 或 Node 直接写盘。
- **合集页账号昵称异步渲染**：`#js_name`/`.nick_name` 常为空，可靠字段是内嵌 `user_name: 'gh_xxx'` 与 `nick_name: '...'`、时间戳 `var ct=`。
- **短链可能被搜索引擎错误关联镜像文章**：以带 cookie 实际渲染出的标题/`gh_id` 为准，勿信第三方镜像。

## 文件地图

- `scripts/wx_clip.mjs` — 端到端可运行脚本（cookie profile → CDP → 抽取 → 下图 → 可选 OCR → Markdown）。
- `references/troubleshooting.md` — 风控/cookie/轮播/WebP/OCR 等踩坑与排查手册。
- `references/output-contract.md` — 产物目录结构、元数据字段、自包含校验与 OCR 清洗规则。
- `scripts/install.sh` — 把本 skill 软链到 `~/.dsh/skills/wx-mp-clip`（实体保留在仓库，单一事实源；幂等，旧实体自动备份）。换机/恢复时执行 `bash scripts/install.sh`。

## 产物契约（摘要）

输出目录自包含：`article.md`（主交付）、`article_fulltext.md`（OCR 全文，图片消息时）、`images/`（正文轮播图 + 封面）、`meta.json`、可选 `ocr_raw.txt`。Markdown 内所有 `images/...` 引用必须在包内存在。完整字段与校验见 `references/output-contract.md`。
