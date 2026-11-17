# 产物契约与校验

## 输出目录结构（自包含）

```
<outDir>/
├── article.md            # 主交付：元信息 +（OCR 全文或配文）+ 图片画廊 + 配文摘要
├── article_fulltext.md   # 图片消息时：OCR 还原的完整正文（按章节整理）
├── ocr_raw.txt           # --ocr 时：Vision 原始识别结果，按 === IMG_xx.png === 分节
├── meta.json             # 结构化元数据
└── images/
    ├── IMG_01.webp … IMG_0N.webp   # 正文轮播 main 图（格式按 magic bytes，常见 webp 1350x1800）
    └── cover_share.jpg             # og:image 分享封面（可选）
```

## meta.json 字段

| 字段 | 含义 | 来源 |
|---|---|---|
| `title` / `shareTitle` | 文档标题 / og:title 分享标题 | `#activity-name` / meta |
| `account` / `ghId` | 公众号昵称 / 原始 ID（`gh_…`） | 内嵌 `nick_name` / `user_name` |
| `publishTs` / `publishTime` | 发布时间戳 / Asia/Shanghai 可读时间 | 内嵌 `var ct=` |
| `caption` | DOM 配文摘要（图片消息时很短，非全文） | `#js_image_desc` / `#js_content` |
| `swiperItems` | 轮播 item 数 | `.share_media .swiper_item` |
| `images[]` | 正文图相对路径（`images/…`） | main 角色图下载结果 |
| `cover` | 封面相对路径 | og:image |
| `hasCaptcha` | 是否命中风控页（true 应直接报错终止） | 页面正则 |
| `sourceUrl` | 原始文章 URL | 入参 |

## 自包含校验（打包前必跑）

```bash
# article.md 里每个 images/... 引用都必须在包内真实存在
grep -oE 'images/[^)]+' article.md | sort -u | while read -r p; do
  [ -f "$p" ] && echo "OK $p" || echo "缺失 $p"
done
```

注意：grep 可能匹配到正文里形如 `IMG_01–07.webp` 的描述文字而误报"缺失"，以真正的 Markdown 图片语法 `![](images/xxx)` 为准；可用更严格的正则 `!\[[^]]*\]\((images/[^)]+)\)` 只取图片链接。

## 打 Markdown 分发包（只含 MD + 依赖图片）

排除 HTML、完整页面快照、风控证据、中间 manifest：

```bash
mkdir -p pkg/images
cp article.md article_fulltext.md meta.json pkg/
cp images/*.webp images/cover_share.jpg pkg/images/   # 按实际格式通配
tar -czf wx_article_markdown.tar.gz -C . pkg
```

## OCR 全文清洗规则

1. 去掉每张卡片重复的页眉（公众号名、@handle、日期）与页脚（slogan、水印、"公众号·xxx"）。
2. 同一开篇卡片的多张重复图（如带/不带水印）只保留一次正文。
3. 还原被卡片换行硬断开的句子为自然段落；保留原有编号列表与小标题（提升为 `##`）。
4. 校正识别噪声：直弯引号统一、英文术语（benchmark / GPQA / SWE-bench / model card 等）核对拼写、明显错字按上下文修正。
5. 在文首注明全文来源为图片 OCR，并保留 `ocr_raw.txt` 作为可追溯原始证据。
6. 文末附公众号名、handle、`gh_id`、卡片日期等出处信息。

## 完成判定（DoD）

- `hasCaptcha=false`，标题与 `ghId` 非空。
- 图片消息：main 图数量 = `swiperItems` 实际正文张数，全部 HTTP 200、magic bytes 与扩展名一致。
- `article.md` 内所有图片链接在包内可解析。
- `--ocr` 时 `ocr_raw.txt` 分节数与正文图数一致，且已产出整理稿。
