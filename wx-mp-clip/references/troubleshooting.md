# 微信抓取与 OCR 排障

按实际失败证据处理。脚本已有有限重试；仍失败时保留图片与底稿，报告具体原因，不能把目录存在或部分文件写出当作成功。

## 1. 命中 wappoc_appmsgcaptcha / 环境异常

先核对最终 URL 和可见页面文本。仅 HTML 脚本中出现同名字符串不能认定风控。

- 脚本每轮从真实 Chrome `Default/Cookies*` 或 `Default/Network/Cookies*` 复制加密数据库，并复制 `Local State`、`Preferences`；cookie 同时放入副本的两处兼容路径。
- 首次命中风控时关闭本次浏览器，重新复制当前真实登录态并重试一次；再次命中就返回非零。无需删除历史 `/tmp/wx_cdp_profile_path.txt`，新版不依赖这个缓存。
- 同一 macOS 用户下由 Chrome 使用自己的凭据解密；不导出明文 cookie，不打印 cookie 值，不操作真实 Chrome 进程。
- 本次样本曾在已有 `poc_sid`、`wxtokenkey`、`wxuin` 的 profile 下直接放行；这只能证明该环境中的登录态可用，不能保证所有出口 IP 或过期会话都能通过。
- 无有效会话或平台继续要求验证时，自动流程有界停止。改 UA、指纹伪装和无限重试不能替代有效登录态；不要求用户手输验证码。

## 2. 0 图，或“有图但漏后半篇”

图片消息正文在 `.share_media` 的轮播条目中。纵向滚动不会保证所有横向卡片创建 `<img>`，因此“滚动后有 7 张图”仍可能不完整。

1. 等待组件就绪后读取 `.share_media .swiper_item[data-src]`，不依赖子 `img` 是否存在。
2. 比较 `extraction.domSwiperItems`、`canonicalItems`、`placeholderItems` 与最终 `images.length`，检查功能区、占位项及 URL 去重的差异。
3. 正式条目不存在时才回退到轮播中的 `img`；普通图文读取 `#js_content img` 的 `data-src` / `currentSrc` / `src`。
4. 图片消息轮播来源最终为空时必须失败，不把短配文输出成完整正文。脚本会等待并重新抽取；结构变化时先在活 DOM 中核实属性和父链，不能靠静态 HTML 的字符窗口猜容器。

真实样本曾有 12 个 `.swiper_item`：1 个占位首图、11 个正式条目。旧逻辑只看到占位首图加前 6 张正式图，共 7 张；后 5 张存在于父条目的 `data-src`，没有子 `img`。补抓应得到 11 张独立卡片，不能为匹配旧基线截断正文。

## 3. 重复开篇 / 带与不带水印的两版首图

优先在来源阶段解决：存在正式 data-src 清单时，排除占位容器。相同资源路径的格式参数变体按规范化 URL 去重。不同路径不按 OCR 相似度自动删除，续页往往共享标题和大量重复术语。

文字整理只去除连续续页重复的章节标题，保留各页正文。

## 4. 下载格式错误、HTML 被存成图片

- 下载必须带 `Referer: https://mp.weixin.qq.com/`；脚本要求 HTTP 200，对下载或格式错误最多重试一次。
- `wx_fmt=png` 和 Content-Type 不能决定文件后缀：校验完整 magic bytes，并用 `sips` 解码尺寸。未知格式或错误页不能落成 `.img` 后继续报成功。
- 原图 `data-src` 与浏览器渲染 URL 可能返回不同表示，例如原图 PNG、渲染图 WebP。保存实际响应并校正后缀即可，不为符合某个历史基线转码。
- 从数组逐张驱动下载，避免 shell 的 `while read` 因末行没有换行漏掉最后一张。

## 5. 账号、标题或发布时间缺失

- 账号优先取内嵌 `user_name: 'gh_…'` 与 `nick_name`；异步昵称 DOM 可能一直为空。
- 时间优先取运行时 `window.ct`，再匹配 `window.ct =`、`var/let/const ct =`，以及 `ori_create_time` / `create_timestamp`。旧版只匹配 `var ct`，因此本次样本漏取。
- `publishTs` 保持数值秒级时间戳，`publishTime` 按 Asia/Shanghai 转换。卡片顶部的日期是设计稿日期，单独记录；没有文章时间时留空并警告。
- 页面标题、分享标题和卡片大标题可能不同。保留 `pageTitle`、`shareTitle`，OCR 识别出首卡标题时再设置 `title` 和 `titleSource`，不把预期标题硬写进脚本。

## 6. 有 ocr_raw.txt，却没有完整文字稿

默认导出保留原图和配文，OCR 文件不属于默认必需产物。只有启用 `--ocr` 时，才应一次生成 `ocr_raw.txt`、`ocr_layout.json`、`article_fulltext.md`，并把识别文字纳入 `article.md`。本机 Apple Vision 的错字和复杂图解排版偏差按辅助结果说明，主要验收仍以完整原图与自包含为准。

- 所有输入先经 `sips` 转 PNG，避免 Vision 对 WebP 的兼容性差异；一次 `swiftc -O` 编译后批量识别。
- 空页或出错页只重试一次，重试关闭语言校正。仍有实际识别错误、分节数不一致、或全部正文为空时返回非零；已下载图片和底稿保留。
- 个别空文字页可能是插图：列出 `ocr.emptyImages` 和警告，不凭字数门槛否定其他有效结果。
- 章节识别使用首行字号与正文比较；首卡允许多行大标题，正文章节只取首行，避免把第一句正文吞进标题。人工复核用坐标底稿核查分段，不按预期章节列表补标题。
- 自动整理不等于逐字校对。引号、图标、脱敏表格和中英文混排仍可能识别不准；保留底稿，对照图核实后再修正。

## 7. 端口冲突或实例残留

新版使用 `--remote-debugging-port=0`，从本次 profile 的 `DevToolsActivePort` 读取 Chrome 实际端口。CDP 建连和请求均有超时，结束时对本次 Chrome 先 SIGTERM、必要时 SIGKILL，再清理本次 profile。不要清理用户 Chrome 或其他任务的临时目录。

## 8. 链接与文章身份不符

短链可能被搜索引擎关联到无关镜像文章。以登录态下实际页面的标题、ghId、时间和原图为准；不把第三方镜像替换进交付。链接失效或缺少文章身份时返回非零。

## 9. 回归与完成状态

先运行 `node --test scripts/wx_clip.test.mjs`，再用真实文章在新目录跑默认导出。核对退出码、`meta.status`、实际图片清单、占位首图去重和自包含检查；涉及 OCR 时再附加 `--ocr` 核对文字稿。失败时已有产物可以保留，但不能标为完成；成功时无需固定为某个图片数量、篇幅或章节数。
