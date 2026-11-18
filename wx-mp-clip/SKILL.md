---
name: wx-mp-clip
description: Export WeChat public-account articles (mp.weixin.qq.com) as self-contained Markdown with local images and optional offline Chinese OCR. Use for clipping articles, image-message carousels, missing lazy-loaded cards, or WeChat verification pages when an existing Chrome login is available.
---

# 微信公众号导出为自包含 Markdown

使用已有 Chrome 登录态读取原页面，默认保存完整原图、配文和来源元数据，生成自包含 Markdown。用户要求 OCR、可搜索或可复制的文字稿时，再加 `--ocr`。默认无人值守，不要求用户打开浏览器、登录或输入验证码。

## 执行

依赖：macOS、Google Chrome、Node.js 22+ 和 `sips`；可选 OCR 还需 `swiftc`。真实 Chrome `Default` 中须有可用微信会话；脚本复制加密 cookie 到本次临时 profile，由 Chrome 自行解密，结束后清理副本。

```bash
# 默认导出；图片消息同样完整保留原图。用户给定的输出目录优先。
node scripts/wx_clip.mjs "https://mp.weixin.qq.com/s/<TOKEN>" ./out

# 用户需要文字稿时启用本机离线 OCR。
node scripts/wx_clip.mjs "https://mp.weixin.qq.com/s/<TOKEN>" ./out --ocr
```

执行前阅读 [产物契约](references/output-contract.md)。运行失败、元数据缺失，或图片数/全文明显不完整时，阅读 [排障手册](references/troubleshooting.md)。

## 抓取与验收规则

- **正文来源**：优先读取活 DOM 中 `.share_media .swiper_item[data-src]`，其地址不依赖 `<img>` 是否已创建。正式条目存在时排除占位首图；同一资源的格式参数变体去重。普通图文回退到 `#js_content img`。
- **标题与时间**：保留 `pageTitle`、`shareTitle`；图片消息识别出首卡大标题后用作 `title`，注明 `titleSource`。发布时间来自 `window.ct` 或脚本时间戳，卡片印刷日期单独记录。
- **图片格式**：带微信 Referer 下载，检查 HTTP 状态、magic bytes 和可解码尺寸。PNG、JPEG、WebP 均可，后缀以响应字节为准。
- **可选 OCR**：`--ocr` 通过本机 Apple Vision 自动生成 `article_fulltext.md`，正文同步纳入 `article.md`。按文字位置恢复段落、列表和章节，保留原始识别与坐标。错字或复杂图解的排版偏差如实说明，原图继续作为阅读依据。
- **失败与重试**：风控只刷新真实 Chrome cookie 副本并重试一次；下载和空 OCR 各有限重试。仍失败返回非零；保留已下载图片与识别底稿。过期登录态无法保证自动恢复，不模拟通过验证码。
- **成功标准**：以完整原图、占位首图去重、来源元数据和包内引用一致为主要验收标准；OCR 是辅助，识别错字不阻断原图交付。明确要求文字稿时，另核对 OCR 分节和实际识别结果。不把固定图片数、字数或章节数写成通用门槛。`verification.json` 保存自动自检结果，最终汇报实际数量、格式、元数据、风控情况及耗时；启用 OCR 时附识别情况。

## 资源与维护

- `scripts/wx_clip.mjs`：抓取、下载、OCR 整理、自包含验证。
- `scripts/vision_ocr.swift`：Vision 批量中文识别，输出文字、位置和置信度。
- `scripts/wx_clip.test.mjs`：本地 Chrome fixture 与离线输出校验回归。
- `scripts/install.sh`：保留现有安装软链流程，不复制第二份技能本体。

修改后执行：

```bash
node --check scripts/wx_clip.mjs
node --test scripts/wx_clip.test.mjs
```

涉及抓取流程的变更，用真实文章在独立目录执行默认导出回归；涉及 OCR 时再验证 `--ocr` 模式。不要把真实 cookie、完整 profile 或私密文章地址提交到 skill 仓库。
