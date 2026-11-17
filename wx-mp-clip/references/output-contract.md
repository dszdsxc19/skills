# 产物契约与校验

## 输出文件

```text
<outDir>/
├── article.md            # 主交付：来源信息、全文、原图画廊、配文摘要
├── article_fulltext.md   # --ocr 自动生成的完整文字稿
├── ocr_raw.txt           # --ocr 原始文字，按 === IMG_xx.png === 分节
├── ocr_layout.json       # --ocr 每页文字、坐标、置信度及识别错误
├── meta.json            # 来源与正文图片清单、运行状态
├── verification.json    # 成功后的自包含检查、OCR 统计、风控情况、耗时
└── images/
    ├── IMG_01.png …      # 正文顺序；后缀可能为 png / jpg / webp
    └── cover_share.jpg   # 可选封面；后缀同样按实际字节确定
```

未加 `--ocr` 时不生成三个 OCR 专用文件。来源文章 URL 和 CDN URL 仅存元数据；两个 Markdown 的链接全部指向包内文件，移动整个目录后仍可阅读。

## 元数据

| 字段 | 契约与来源 |
| --- | --- |
| `title` / `titleSource` | 默认页面标题；图片消息识别出首卡大标题时采用 OCR 标题，并记录图片路径 |
| `pageTitle` / `shareTitle` | 原始 DOM / og:title 标题，保留与卡片标题的差异 |
| `account` / `ghId` | 内嵌 `nick_name` / `user_name`，不是异步空节点 |
| `publishTs` / `publishTsSource` | 数值秒级时间戳及实际取值来源，优先 `window.ct`，其次脚本赋值或 `ori_create_time` / `create_timestamp` |
| `publishTime` | Asia/Shanghai 时间，形如 `2026-11-15 22:26:54+08:00`；缺失时留空并警告 |
| `bodyInImages` | 是否为轮播图片消息 |
| `caption` | DOM 配文；图片消息中与 OCR 全文分开保留 |
| `swiperItems` | 去重、排除占位项后实际待导出的正文图片数，与 `images.length` 一致 |
| `extraction` | 原 DOM 节点数、正式 data-src 条目数、占位项数、URL 去重数 |
| `images[]` / `imageDetails[]` | 正文相对路径；每张图的来源 URL、HTTP 状态、格式、宽高、字节数、SHA-256 |
| `cover` / `coverDetails` | 可选封面相对路径及同样的下载证据 |
| `hasCaptcha` / `captchaEncountered` | 最终页面是否为风控页 / 本轮是否曾命中；前者为 true 时不能成功 |
| `ocr` | 图片数、重试数、空文字页、章节标题、字数、卡片日期与署名 |
| `sourceUrl` | 原始文章 URL |
| `status` / `warnings` / `error` | 运行中、成功或失败：`processing` / `completed` / `failed`；警告与失败原因 |

字数统计排除 Markdown 标题标记、列表序号和空白；同时记录 `nonWhitespaceCharacters` 与 `hanCharacters`，避免把“字数”误读为同一种口径。章节数不包括文章总标题和无标题开篇导语。

## 图片来源与去重

1. 按正式 `.share_media .swiper_item[data-src]` 的 DOM 顺序导出全部来源，不能以已出现的 `<img>` 数量代替。
2. 正式条目存在时忽略 `img_item_placeholder` 所在的占位容器，其首图经常与正式第 1 张正文重复。
3. URL 去重只移除 `wx_fmt`、`from`、`wxfrom`、`tp`、`usePicPrefetch`、`watermark` 等表示参数，保留其他查询参数。不同路径的卡片不做文本相似度去重，避免误删续页。
4. 每张下载图片必须 HTTP 200，且可解码出宽高；后缀按 WebP `RIFF…WEBP`、JPEG `FFD8FF`、PNG `89504E470D0A1A0A` 决定。

## 自动文字整理及边界

- Vision 在统一 PNG 输入上批量识别；保留每张卡片的独立原始分节与坐标。
- 根据账号、署名、日期的位置识别页眉区域；根据底部文字位置移除水印、slogan。卡片日期单独记入 `ocr.cardDates`，不替代发布时间。
- 根据字号推断首卡多行标题和后续章节首行；相邻续页的同名章节只保留一个标题。使用行间距合并硬换行，保留编号列表与表格单元格的分隔。
- 排版是启发式处理，不做无依据的错字替换或内容补写。复杂表格、引号和低清文字可能仍有 OCR 误差；核对时查看原图、`ocr_raw.txt` 和 `ocr_layout.json`。
- 没识别到文字的图片重试一次后记入 `emptyImages`；有文字的其余页仍可导出，并明确警告。全部正文为空或识别发生实际错误则失败，底稿继续保留。

## 自动验收与回归

脚本成功前检查：必要文件齐全、图片后缀匹配、正文清单与文件一致、两个 Markdown 没有包外或缺失引用；启用 OCR 时分节数与正文图数一致。通过后写 `status: completed` 和 `verification.json`，返回 0。

```bash
node --check scripts/wx_clip.mjs
node --test scripts/wx_clip.test.mjs
node scripts/wx_clip.mjs "https://mp.weixin.qq.com/s/<TOKEN>" ./regression --ocr
```

2026-11-18 对「阿东玩AI」benchmark 图片消息的实际来源核验：11 张独立正文卡片，另有 1 个占位首图节点；原始 CDN 响应为 1350×1800 PNG，封面为 1280×1706 JPEG。正文有 7 个章节和开篇导语。旧记录的“7 张 WebP、约 1500 字、4 章”来自不完整抓取，不作为固定验收门槛。时间戳 1794752814 对应 2026-11-15 22:26:54+08:00，卡片印刷日期为 2026-11-14。

重跑同一目录时，仅移除上一份元数据明确拥有且本次已替换的生成文件，保留用户自有文件。回归通常使用新目录，避免与旧产物混淆。

分发时复制整个成功输出目录即可；不要把 Chrome profile、cookie、静态 HTML 或排障页面快照混入包内。
