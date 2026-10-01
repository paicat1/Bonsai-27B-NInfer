# 模型实机产出（Demo Gallery）

> **这些 HTML 全部由 Bonsai-2-27B（三元量化）模型在本机实机跑出来的，不是人手写的工程代码。**
> 它们是"三元量化后智力不塌"（PPL 6.1129，判据 ≤6.8）的**侧证**——模型能独立写出现在就能跑的图形程序。

## 怎么看

GitHub 不会执行仓库里的 HTML，点开链接只会看到源码。**要本地看效果，两种方式**：

**方式一：直接双击**（推荐，五个纯 SVG 作品零依赖，双击即开）

```
docs/demos/dragonfly-clock.html
docs/demos/clock-dragonfly.html
docs/demos/pelican-night-ride.html
docs/demos/squirrel-bucket.html
docs/demos/lighthouse-storm.html
```

**方式二：起本地服务器**（两个 Three.js 3D 作品必须这样，因为 ES module / WebGL 在 `file://` 下会被浏览器策略拦）

```powershell
cd docs/demos
python -m http.server 18899
# 浏览器打开 http://127.0.0.1:18899/mech-bee.html
```

两个 3D 作品的 `three.min.js` 已随目录入库，**离线可用**；`mech-bee.html` 另有三个 CDN 兜底源（本地缺失时自动降级）。

## 作品清单

| 文件 | 标题 | 技术 | 体积 | 外部依赖 |
|---|---|---|---|---|
| [`lighthouse-storm.html`](lighthouse-storm.html) | Lighthouse Storm · 灯塔风暴 | Canvas 2D | 14.5 KB | 无 |
| [`mech-bee.html`](mech-bee.html) | 机械蜜蜂 · Three.js 交互 | Three.js（几何体全构建） | 25.2 KB | `three.min.js`（已入库） |
| [`aegis9-truck.html`](aegis9-truck.html) | AEGIS-9 未来工业重型机械卡车 | Three.js | 22.1 KB | `three.min.js`（已入库） |
| [`dragonfly-clock.html`](dragonfly-clock.html) | 蜻蜓钟表 | 纯 SVG + CSS | 5.2 KB | 无 |
| [`clock-dragonfly.html`](clock-dragonfly.html) | 老式机械钟表上的蜻蜓 | 纯 SVG + CSS | 9.4 KB | 无 |
| [`pelican-night-ride.html`](pelican-night-ride.html) | 鹈鹕夜骑 · 夜路 SVG 动画 | 纯 SVG + CSS | 13.1 KB | 无 |
| [`squirrel-bucket.html`](squirrel-bucket.html) | 松鼠手摇提桶 | 纯 SVG + CSS | 8.8 KB | 无 |

截图见 [`../images/demos/`](../images/demos/)。

## 已知缺陷（如实记录，未擅自修改）

**`aegis9-truck.html` 控制台报 13 条 `THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN`**，症状是**甲板货箱组不渲染**（其余部件——驾驶室、发动机、排气管、6 轮、后视镜、蒸汽烟囱——均正常）。

[EVIDENCE] `docs/demos/aegis9-truck.html` 浏览器控制台：`Hl @ three.min.js:6` ×13；截图 `../images/demos/aegis9-truck-20261001.png` 可见货箱缺失。

根因未定位（某处几何体顶点算出 NaN），**这是模型生成代码的真实 bug，保留原样作为实机记录**。

## 第三方代码

`three.min.js` — Three.js r158，**MIT License**：

```
Copyright 2010-2023 Three.js Authors
SPDX-License-Identifier: MIT
```

（许可声明在文件头部，随文件一并入库。）

## 原始产出位置

这些文件最初散落在作者的临时测试目录，入库时统一改名为 ASCII 文件名以便跨平台引用，内容**未做任何修改**：

| 仓库内文件 | 原始路径 |
|---|---|
| `mech-bee.html` | `J:\测试目录随时清空\mech-bee.html` |
| `aegis9-truck.html` | `J:\测试目录随时清空\future-truck\index.html` |
| `clock-dragonfly.html` | `J:\测试目录随时清空\clock-dragonfly.html` |
| `three.min.js` | `J:\测试目录随时清空\three.min.js` |
| `dragonfly-clock.html` | `J:\测试目录\蜻蜓钟表.html` |
| `pelican-night-ride.html` | `J:\测试目录\鹈鹕夜骑.html` |
| `squirrel-bucket.html` | `J:\测试目录\松鼠手摇提桶.svg.html` |
| `lighthouse-storm.html` | `C:\Users\PC\.dsh\ungrouped\lighthouse-storm.html` |

未收录：`fluid.html`（WebGL 流体，作者反馈当时尚未跑完）。
