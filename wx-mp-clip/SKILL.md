---
name: wx-mp-clip
description: Export WeChat public-account articles (mp.weixin.qq.com) as self-contained Markdown with local images and optional offline Chinese OCR. Use for clipping articles, image-message carousels, missing lazy-loaded cards, or WeChat verification pages when an existing Chrome login is available.
---

# 微信公众号导出为自包含 Markdown

使用已有 Chrome 登录态读取原页面，下载完整正文图片；图片消息加 `--ocr`，一次生成原始识别结果和自动整理的完整文字稿。默认无人值守，不要求用户打开浏览器、登录或输入验证码。

## 执行

依赖：macOS、Google Chrome、Node.js 22+；OCR 还需 `swiftc` 和 `sips`。真实 Chrome `Default` 中须有可用微信会话；脚本复制加密 cookie 到本次临时 profile，由 Chrome 自行解密，结束后清理副本。

```bash
# 路径以本 skill 所在目录为基准；用户给定的输出目录优先。
node scripts/wx_clip.mjs "https://mp.weixin.qq.com/s/<TOKEN>" ./out --ocr

# 不需要图片文字稿的普通图文可省略 --ocr。
node scripts/wx_clip.mjs "https://mp.weixin.qq.com/s/<TOKEN>" ./out
```

执行前阅读 [产物契约](references/output-contract.md)。运行失败、元数据缺失，或图片数/全文明显不完整时，阅读 [排障手册](references/troubleshooting.md)。

## 抓取与验收规则

- **正文来源**：优先读取活 DOM 中 `.share_media .swiper_item[data-src]`，其地址不依赖 `<img>` 是否已创建。正式条目存在时排除占位首图；同一资源的格式参数变体去重。普通图文回退到 `#js_content img`。
- **标题与时间**：保留 `pageTitle`、`shareTitle`；图片消息识别出首卡大标题后用作 `title`，注明 `titleSource`。发布时间来自 `window.ct` 或脚本时间戳，卡片印刷日期单独记录。
- **图片格式**：带微信 Referer 下载，检查 HTTP 状态、magic bytes 和可解码尺寸。PNG、JPEG、WebP 均可，后缀以响应字节为准。
- **OCR**：`--ocr` 自动生成 `article_fulltext.md`，正文同步纳入 `article.md`。按文字位置恢复段落、列表和章节，移除页眉页脚、续页重复标题；保留原始识别与坐标。自动整理不承诺消除全部错字，疑似错字对照图片核实，不能据上下文补造。
- **失败与重试**：风控只刷新真实 Chrome cookie 副本并重试一次；下载和空 OCR 各有限重试。仍失败返回非零；保留已下载图片与识别底稿。过期登录态无法保证自动恢复，不模拟通过验证码。
- **成功标准**：以实际轮播来源清单、下载文件、OCR 分节和包内引用一致为准，不把固定图片数、字数或章节数写成通用门槛。`verification.json` 保存自动自检结果。最终汇报实际数量、格式、OCR 字数/标题、元数据、风控命中情况及耗时。

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

涉及抓取或 OCR 流程的变更，还需用真实文章在独立输出目录执行一次 `--ocr` 回归。不要把真实 cookie、完整 profile 或私密文章地址提交到 skill 仓库。
