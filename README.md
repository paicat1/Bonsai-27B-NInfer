# Bonsai-NInfer — RTX 5080 三元量化复现指南

> 本仓库在 **RTX 5080（16GB）** 跑通了 **Bonsai-2-27B 三元量化模型**（`Ternary-Bonsai-2-27B.ninfer`）。
> 名字"4090"是上游沿用，**本 fork 实测平台是 5080**。
> 这份 README 是**复现索引**：每一步要去看什么（文件/命令/报告/源码位置）都列出来，
> 让复现者**自己照着查证推进**，而不是靠我口头转述。

---

## 0. 先看这四样（搞清楚全貌再动手）

| 要看什么 | 在哪 |
|---|---|
| 完整开发史（M0–M8：M0–M7 核心落地 + M8 09-22 后优化线） | Bonsai 主库 `docs/项目构建史.md` |
| 技术论文《三元-Bonsai-27B-NInfer-移植》 | `三元-Bonsai-27B-NInfer-移植-技术论文-20260920.pdf` |
| 作者工具链说明 docs/01–04 | `landing/tools/ninfer-ada-ternary/docs/` |
| 各里程碑报告（M0–M6 + CraneBW + A/B） | Bonsai 主库 `docs/reports/` |

---

## 一、我们要复现的东西

**16GB 卡 + 2.125bit 三元量化跑 27B**，智力不塌（PPL 6.1129）、显存可控、256K 长上下文可跑。

## 二、7 步复现路线（每步标明"要看什么"）

### 第 1 步 · 锁定来源
- **要看的**：构建史 §2 上游血统表；作者 ModelScope 仓 `shensanshu/ninfer-ada-ternary`；基线 `Ambolio/ninfer-4090-windows @ 6eb70a0`。
- 关键：补丁基线 = **Ambolio v1.0.8**，不是官方线。工具仓锁 commit（pack.py 拒绝非 groupwise-int 模板那版）。

### 第 2 步 · 下载权重（~70GB）
- **要看的**：HF `prism-ml/bonsai-2`；量化 GGUF 清单（PQ2_0 7.2G / PTQ1_0 5.9G / mmproj）；DFlash2 组件。
- **要看制品代际**：`<制品>.ninfer` magic 字节，确认引擎代。我们的 = 02（v2，与 v1.0.8 自洽）。

### 第 3 步 · 打包模板 + 三元制品
- **要看**：作者工具链 `landing/ninfer-ada-ternary/`（docs/01-04 + patches + `pack.py` + `MAPPING.json` + `verify`）。
- 产物（本机已有，可对照）：
  - 模板 `landing/artifacts/qwen3_8_27b.ninfer`（19.03 GiB/1190 对象）+ 它的 `qwen3_8_27b.ninfer.conversion.json`（转换报告，看配置）
  - 三元 `landing/artifacts/Ternary-Bonsai-2-27B.ninfer`（9.81 GiB/1192 对象）
  - `bonsai2-hadamard-meta.json`（折叠基变换元数据）
- **坑（发布缺件）**：作者包缺 `numeric.py` / `_ternary_ref.py` → 用运行时 shim `landing/tools/ternary_shim.py`，**不改上游**。
- 六项验证链（pack check/build/payload_order/signs/row_order/assembly）必须全 PASS。

### 第 4 步 · 构建引擎（M4）
- **要看**：
  - 基线 `build_v1.0.8.bat`（构建配方）
  - 基线 `CMakeLists.txt` **L59-62**（CUDA ≥13.1 硬门）、**L82-85**（仓根 `ffmpeg\` 硬依赖）
  - `device.h`（非 sm_89 的 `#error` 守卫）→ 改 CMake 架构列表 `89|120a`
  - 用 `cuobjdump` 验 **sm_120a SASS**（防 JIT 伪装）
- 本报告用 CUDA 13.3 旁装，构建目录 `_build_5080`。

### 第 5 步 · 验收（M5）
- **要看**：报告 `M5端到端验收报告`；`report.json`（PPL 原始值）。
- 判据：PPL ≤6.8（越低越好），我们 6.1129。
- 显存账本三场景，验证占用与账面吻合。

### 第 6 步 · 速度标定（M6）
- **要看**：`M6` 报告 + 三档验证脚本。
- 5080 实测演进：裸 decode 68 → MTP → DFlash2 英文 104.7（中文负收益）。**后续经用户实测大幅提升**，见第三节档位表（224K+MTP3 峰值 250、128K+DFlash7 峰值 355、S8 内核 prefill 2.85k/峰值解码 396）。

### 第 7 步 · 提速内核（M7 + 后续）
- **要看**：`CraneBW/ninfer-ternary-bonsai-ada`（比对 `verify`）；合并方案 `CraneBW内核合并方案`；报告 `CraneBW内核合并验证报告`。
- 结果：prefill 600→1288；后续 s8/wide_t 移植 → **冷 prefill 最高 2.85k**（S8 内核，启动器 prefill 下拉可选）。
- **坑**：CraneBW 声称 8 文件，漏合 `gemv.cuh`（新 kernel 未并）→ 首编 12 error。逐文件核对，别信"x 个文件"。

---

## 三、起服与档位（要看：serve --help / BAT 参数）

- 一套 BAT 在 Bonsai 主库，命令要点见下表：

| 档位 | 命令要点 | 5080 实测 |
|---|---|---|
| **启动器默认（现行）**<br>`--kv-dtype nvfp4 --kv-capacity 184320 --max-context 184320 --spec dflash2 --draft-tokens 7 --lm-head-draft` | 同左 | **10-01 真实负载配对**：端到端 **230~245 tok/s**、解码峰值 **303 t/s**、prefill 最高 2.68k tok/s |
| **启动器省显存档**<br>同上但 `--spec mtp --draft-tokens 3`（去 `--lm-head-draft`） | 同左 | 端到端 **195 tok/s**、解码稳 118~182 t/s，**比 DFlash2 少占 1.65 GiB**（草稿权重 7.45 vs 9.10 GiB） |
| 日常 FP8 | `--kv-dtype fp8 --spec mtp --draft-tokens 2 --max-concurrency 2` | 均值 114.3 t/s |
| 224K MTP3 | `--max-context 229376 --kv-dtype k8v4 --spec mtp --draft-tokens 3`（MMA 预填充内核） | 峰值 250 t/s / 均值 180 t/s / prefill 1.3k tok/s |
| 128K DFlash7 | `--max-context 131072 --kv-dtype bf16 --spec dflash2 --draft-tokens 7 --lm-head-draft` | 峰值 355 t/s / 均值 225 t/s / prefill 1.4k tok/s；日常工作 180-280 t/s |
| DFlash2 英文 | `--spec dflash2 --draft-tokens 7 --lm-head-draft` | 139.5（中文勿用）|

> **S8 内核更新后（更快）**：prefill 最高 **2.85k tok/s**，峰值解码**摸到 396 t/s**（MMA/S8 内核对比见启动器 prefill 下拉）。
> **口径提示（10-01 校准）**：日志有两种统计口径，数值不同——**5 秒窗口口径**（`throughput \| 5.0s` 行）能捕捉请求中途瞬时峰值，**整请求口径**（`req#N done` 行）是请求级平均。78 份日志窗口口径实测：**prefill 极值 2,660**（4 份日志共同触到，是硬天花板）、**decode 极值 396.9**（`serve_20260926_222420.log`，k8v4/131072 档，窗口连续三条 396.4/396.9/396.7）。**故上条「摸到 396 t/s」有日志支撑，准确。** 整请求口径下 prefill 可达 2,740。**2.85k 在两种口径下均无日志支撑，保留不改**——推测为客户端 UI 瞬时计数与引擎窗口采样起点不同，**未取证**。

- **投机档位（10-01 定案）**：`--spec dflash2 --draft-tokens 7 --lm-head-draft` = 速度优先（启动器默认）；`--spec mtp --draft-tokens 3` = 省显存。**K 越大不一定越快**：DFlash2 `K>=10` 断崖式崩塌（比不开投机还慢 70%+，属禁用区），MTP `K=1~5` 吞吐基本持平。判据必须是**端到端吞吐**（Σoutput/Σtotal），不是单请求 decode 均值（受输出长度偏置）；**接受率是强内容依赖指标，不能用合成填充文本测**（同档跨内容差 2.5 倍）。
- **`--prefill-chunk`（10-01 三档扫描）**：默认 **1024 即甜点**。256 是坑（prefill **−40%**，小 chunk 让 prefill 单元边界往返放大 4 倍）；4096 与 1024 打平（+0.9%）但 KV runtime 多占 **0.68 GiB**。短 prompt 上该参数被 `min` 钳位为空操作。
- **日志统计纪律（10-01 血泪）**：① **进行中的日志一律不报**——serve 未退出时统计会得到残缺值（曾把 340 请求/186.7 tok/s 误报成 108 请求/110.6 tok/s，低估 69%）；报数前先确认端口无监听 + 日志 mtime 静默 ≥5 分钟。② **两种口径不可混用**，极值一律按 5 秒窗口口径。③ **配对结论必须同档 + 同内容 + 同规模**，仅 spec 不同的三轮对照才是干净配对。

- 每个档位**要看对应 BAT 的完整参数**（`起服-*.bat` 就是现成样板，改路径即用）。
- 具体参数语义看 `ninfer-serve --help`。

## 四、坑汇总（每坑标"去看什么"）

| 坑 | 现象 | 要看/对策 |
|---|---|---|
| 制品代际 | 引擎不认/乱码 | 看 `--help` 认代际 + magic 字节 |
| 发布缺件 | 打包失败 | `landing/tools/ternary_shim.py`（写 shim 不改上游）|
| 视觉 | 引擎已支持 `--vision`（内置视觉塔 + media），启动器有"视觉"开关 | 启动器 GUI 把视觉拨到"开启"即可（或 BAT 加 `--vision`）；默认档位关闭 |
| arch 守卫 | 非 sm_89 `#error` | 看 `device.h` + CMake 架构列表 |
| ffmpeg / CUDA | 编不过 | 基线 CMakeLists L59/L82 |
| CraneBW 漏合 | 首编 error | 逐文件核对，别信"x 个文件"|
| 并发挤爆 | `preparing CUDA graphs bad alloc` | 小余量档并发 1 |
| 思考空收尾 | 长思考无正文 | 已修：commit `145bccb`（frontend 强制进正文）|
| Agent 死循环 | "继续"失忆 | 恢复会话/投喂材料，别靠思考帽 |

## 五、关键文件索引（本仓库可直接查）

| 文件 | 看什么 |
|---|---|
| `landing/artifacts/Ternary-Bonsai-2-27B.ninfer` | 三元制品 |
| `landing/artifacts/qwen3_8_27b.ninfer` + `.conversion.json` | 模板 + 转换报告 |
| `landing/tools/ternary_shim.py` | 三元运行时 shim |
| `landing/tools/ninfer-ada-ternary/` | 作者工具链 |
| `*起服-*.bat` | 各档位现成命令 |
| `docs/项目构建史.md`（主库）| 逐日全史 |

---

**说明**：本仓库是 Bonsai-2-27B 三元部署的复现工程；上游作者工作看上游，这里列的是"我们怎么跑起来的每一步，要去看什么资料/命令"。

> **两分支配合**：本项目 = 同一仓库两个分支一体——本分支（`engine-main`）= 引擎代码与复现索引；项目层（启动器/BAT/构建史/报告/论文/制品）在 `main` 分支，见那边根目录 `README.md`。