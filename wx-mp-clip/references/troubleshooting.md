# 排查手册（实测踩坑）

## 1. 风控验证页 wappoc_appmsgcaptcha（"环境异常，完成验证后即可继续访问"）

- **根因**：判定依据是「出口 IP + 会话 cookie」，不是 headless/UA/`navigator.webdriver`。数据中心 IP（如 AWS 段）下的无 cookie 会话必拦；带真实微信登录 cookie 的 headless 会话直接放行。
- **修法**：
  1. 确认本机真实 Chrome 已登录微信网页/公众号，`Default/Cookies` 里有 `poc_sid`/`wr_skey`/`wxtokenkey`/`wxuin`。
  2. 用脚本的 `ensureCookieProfile()` 复制 `Default/Cookies*` + `Local State` + `Preferences` 到临时 `--user-data-dir`。macOS 同用户共享 keychain 的 "Chrome Safe Storage" 密钥，Chrome 自行解密，**不要手工导明文 cookie**。
  3. Cookies 同时放 `Default/` 与 `Default/Network/`，兼容不同 Chrome 版本。
  4. cookie 过期会再次命中验证页：删除 `/tmp/wx_cdp_profile_path.txt` 与临时目录，重跑即自愈重建。
- **不要**靠改 UA、加指纹伪装、Playwright stealth 解决——实测对这个门无效。

## 2. 图片抓到 0 张 / 正文图全漏

- 微信「图片消息」把正文放在 `.share_media` 轮播组件，不在 `#js_content` 内；只查 `#js_content img` 必然为 0。
- 懒加载：图在 `data-src`，不滚动不填充。先 `for y in 1..10: window.scrollTo(0, y*900); await sleep(300)`，再回到顶部。
- 角色判定：对每张 mmbiz `img` 向上遍历 7 层父节点收集 `className`：
  - 命中 `avatar|head_img|qrcode|wx_follow|jump_author` → 头像/二维码，跳过；
  - 命中 `swiper_function_area|swiper_tag_wrp` → 功能区标签图（静态正则易把它误判成正文，活 DOM 父链为准）；
  - 命中 `swiper_item_img|swiper_item|share_media|swiper_content` → **正文 main 图，保留**。

## 3. 静态 HTML 正则误判容器

- 类名 `share_media`、`swiper_item_img` 等同时出现在顶部 `<style>` CSS 与 DOM 节点；`indexOf('share_media')` 可能命中 CSS。
- 固定字符窗口回溯父容器会因间距变化把 main 误判成 tag。
- **结论**：以渲染后活浏览器的 `element.parentElement` 链为权威，别对保存的静态 HTML 用位置窗口正则。

## 4. 下载的图扩展名/格式不对

- URL 里 `wx_fmt=png` 不可信；实测响应 `Content-Type: image/webp`，`file` 显示 RIFF Web/P。
- 必须带 `Referer: https://mp.weixin.qq.com/`，否则 mmbiz CDN 拒绝。
- 按 magic bytes 定扩展名：前 4 字节 `RIFF`→`.webp`；`FF D8`→`.jpg`；`89 50 4E 47`→`.png`。

## 5. shell 循环漏掉最后一张图

- `while read -r line; do ...; done < list.txt` 当末行无换行符时不执行最后一条。
- 用 `while read -r line || [ -n "$line" ]; do ...; done`，或干脆在 Node 里 `writeFileSync` 后用数组驱动下载。

## 6. 合集/图片消息页账号昵称为空

- `#js_name`、`.nick_name`、`.wx_user_profile_nickname` 多为异步渲染，headless 无交互时是空 span，长轮询也未必填充。
- 可靠来源是内嵌 JS：`user_name: 'gh_xxxxxxxx'`（原始 ID 必有）、`nick_name: '公众号名'`、发布时间戳 `var ct = "1794752814"`（`new Date(ts*1000)` 按 Asia/Shanghai 换算）。
- 时间戳换算示例：`TZ=Asia/Shanghai date -r 1794752814`。

## 7. OCR（Vision）

- Vision 对 WebP 输入兼容性不稳，先 `sips -s format png x.webp --out x.png`。
- Swift 注意赋值号两侧空格一致（`req.recognitionLevel = .accurate`，写成 `=.accurate` 会编译报错 `'=' must have consistent whitespace`）。
- 建议 `swiftc -O` 编译成二进制再批量跑，避免逐图解释启动开销。
- 识别噪声：每张卡片重复的页眉（公众号名/handle/日期）、页脚（"多搜索、多动手、多思考 | Vibe Anything"、公众号水印）需去重；弯引号 `“”` 可能识别成直引号；`gh`/英文混排偶有错字，按上下文人工或规则校正。
- 轮播第 1、2 张可能是同一开篇卡片（其一带水印），整理全文时不要重复计。

## 8. 短链与镜像文章错配

- 搜索引擎可能把短链错误关联到无关镜像文章（本任务曾被关联到一篇"软暴力"司法解释镜像，实际是 Agent/benchmark 主题）。
- 一律以带 cookie 实际渲染页的标题 + `gh_id` + 内容为准；第三方镜像仅作隔离对照，不进交付。

## 9. 端口/实例冲突

- 自建 CDP 实例用随机高位端口（脚本取 9300–9800），不要复用已存在但 target 为空的 9222 临时实例。
- 结束时 `SIGTERM` 再 `SIGKILL` 清理 headless 进程，避免残留占用 profile 锁。
