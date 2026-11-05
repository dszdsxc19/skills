# 运行与时间轴

## 项目起点

`scripts/scaffold.py` 将可运行示例复制到新目录，保留现有非空目录。模板、字体、许可和钢琴采样均随 Skill 提供，不依赖上一次聊天或个人项目路径。

将 `miniature_skill` 设为当前 `SKILL.md` 所在目录。

```sh
set -e
miniature_skill=/absolute/path/to/miniature-explainer-video
python3 "$miniature_skill/scripts/doctor.py"
python3 "$miniature_skill/scripts/scaffold.py" /absolute/path/to/project
cd /absolute/path/to/project
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python prepare.py
blender -b --python-exit-code 1 --python scene.py
blender -b scene.blend --python-exit-code 1 --python render.py
.venv/bin/python score.py
.venv/bin/python compose.py --stills --movie
.venv/bin/python verify.py
```

`uv` 可替换为当前已配置的虚拟环境与包管理器。Blender 和 FFmpeg 为系统工具，Pillow、NumPy、SciPy、fonttools、可选 TTS 包属于项目依赖。`doctor.py` 列出 PATH 内全部候选位置与当前版本；不会安装软件。

当前实测环境为 Blender 5.2.2、Python 3.12、FFmpeg 9.0.2。其他版本先运行工具盘点和短例验证，按实际 API 修正兼容项。

示例为包裹分拣。正式片应替换题材、资产、分镜、声音和图文；先看 `project.json`，它是当前脚手架的输入样例。

## 输入与输出的语义

`project.json`：

- 顶层 `width`、`height`、`fps` 是输出规格。
- `narration.provider` 为 `none`、`edge` 或 `file`。`none` 使用人工规划时长；`edge` 请求 TTS；`file` 使用既有录音。
- `segments` 保存旁白段。`duration` 为可选的段长；缺省时由真实音频加前后留白确定。文本、音色、速度改变会生成新的缓存键。
- 录音段使用 `audio_file`；可提供 Edge 格式的 `timing_file`，或人工核对的 `manual_cues`。没有词时间时按段级精度记录。
- `anchors` 是词语锚点；同一文本重复时可用 `{"text":"词语","occurrence":2}` 明确第几次。
- `shots` 通过 `segment`、`in`、`out` 指向旁白段内的范围，`out:"end"` 表示到该段结束。一段旁白可以拆成多个镜头。
- 镜头 `id` 用于文件和引用，`label`、`headline` 是面向观众的文字；不把内部标识直接当作画面文案。
- 镜头 `beats` 使用 `at` 表示镜头内的相对秒数，或 `cue` 引用 `段ID.锚点名`。`duration` 描述动作范围，`kind` 供动画和声音选择使用。
- 镜头 `mode` 为 `3d` 或 `graphic`。纯二维镜头在 `compose.py` 中实现，无需生成 Blender 帧。

`prepare.py` 生成 `timeline.json`，包括实际段长、镜头范围、字幕、时间精度、命名事件与帧数。3D、图文和声音读取该文件，不重新估算口播时间。

模板的时间是秒；帧索引是从零开始、右端不包含。Blender 的帧号为 `index + 1`。镜头边界落在输出帧格上；所有镜头连续覆盖成片，缺帧和重叠需要处理后再合成。

## 音频与时长

指定了段长但音频放不下时，脚本保留已取得的音频并报出冲突。按用户目标选择改稿、重录或调整时长，避免自动截断。

TTS 元数据只支持它真实提供的精度。缺词时间时，用段级同步或明确的人工锚点；不可把按字数插值的时间称为词级时间。

字体准备生成完整的静态中文字体，避免新题材出现缺字；屏幕图文使用随项目提供的可变字体。素材许可保存在 `assets/`。

## Blender 与分段恢复

`scene.py` 在新后台进程里建立场景并烘焙动画；不会接管用户当前窗口。

`render.py --shots shot-a,shot-b` 只渲选中的镜头。每个镜头的目录带渲染来源摘要，清单 `render/manifest.json` 显式指向各镜头的版本；失败重跑复用同源有效帧。

共享模型、灯光或机位改变时，重渲所有受影响镜头。局部修正可以只替换相应镜头，旧目录保留。清单记录实际来源，不把旧镜头写成新工程生成。

逐帧 PNG 可能包含渲染日期和耗时等元数据。检查同源重渲的一致性时比较像素，文件摘要变化本身不能证明画面变化。

只改标题、字幕、图文或音轨时，保留三维帧，重新运行相应合成步骤。改时长或镜头边界时先更新 `timeline.json`，随后检查分段清单与帧范围。

## 可编辑交付

交付 `scene.blend`、`project.json`、`timeline.json`、场景与图文脚本、独立音轨和素材署名。Blender 工程包含三维关键帧；图文、字幕与声音的编辑入口在各自脚本及时间轴中。

包内可不包含大量逐帧 PNG；应保留重建命令与实际验证报告。交付前在不依赖旧聊天目录的工作目录中至少完成一次短片链路验证。
