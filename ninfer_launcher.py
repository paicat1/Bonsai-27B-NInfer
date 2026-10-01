# -*- coding: utf-8 -*-
"""NInfer 图形界面启动器：用鼠标点选参数搭配，实时预览命令并启动 serve。

零外部依赖（仅 Python 自带 tkinter）。双击 启动器.bat 即弹窗口。
"""
import json
import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, simpledialog

# ---------------------------------------------------------------
# 常量：路径与基础参数
# ---------------------------------------------------------------
BASE_DIR     = r"J:\Bonsai\landing\repos\ninfer-4090-windows"
BUILD_DIR    = os.path.join(BASE_DIR, "_build_5080")
APPS_DIR     = os.path.join(BUILD_DIR, "apps")
ARTIFACT     = r"J:\Bonsai\landing\artifacts\Ternary-Bonsai-2-27B.ninfer"
CONFIG_FILE  = os.path.join(r"J:\Bonsai", "ninfer_launcher_profiles.json")
PORT_DEFAULT = 18787
# 模型选择：正常 + CRACK(去审查版) 两个独立制品（artifacts 目录 gitignore 不入库）
MODEL_OPTIONS = {
    "normal": ("正常(Bonsai 三元)", r"J:\Bonsai\landing\artifacts\Ternary-Bonsai-2-27B.ninfer"),
    "crack":  ("CRACK(去审查版)",  r"J:\Bonsai\landing\artifacts\Bonsai-2-27B-CRACK.ninfer"),
}
# serve_tee 必须用 python.exe（带控制台窗口）来显示日志，不能用 pythonw：
# 本启动器 GUI 用 pythonw 运行时 sys.executable 指向 pythonw.exe，用它启动
# serve_tee 会得到无控制台窗口，日志无法显示在 CMD 窗口（只会落盘）。
PYTHON_EXE   = r"D:\Python311\python.exe"

# ---------------------------------------------------------------
# 维度定义：key -> {value: (显示名, 附加参数列表)}
# ---------------------------------------------------------------
BUILD_OPTIONS = {
    "new": ("新版(A+B, apps)", os.path.join(APPS_DIR, "ninfer-serve.exe")),
    "old": ("旧版(09-22, 根)", os.path.join(BUILD_DIR, "ninfer-serve.exe")),
}
KV_OPTIONS = {
    "fp8":      ("fp8",      ["--kv-dtype", "fp8"]),
    "bf16":     ("bf16",     ["--kv-dtype", "bf16"]),
    "int8":     ("int8",     ["--kv-dtype", "int8"]),
    "nvfp4":    ("nvfp4",    ["--kv-dtype", "nvfp4"]),
    "k8v4":     ("k8v4",     ["--kv-dtype", "k8v4"]),
    "rk4v4":    ("rk4v4",    ["--kv-dtype", "rk4v4"]),
    "rk4v4-e8": ("rk4v4-e8", ["--kv-dtype", "rk4v4-e8"]),
}
CTX_OPTIONS = {
    "32k":  ("32K",   ["--max-context", "32768"]),
    "128k": ("128K",  ["--max-context", "131072"]),
    "150k": ("150K",  ["--max-context", "153600"]),
    "160k": ("160K",  ["--max-context", "163840"]),
    "170k": ("170K",  ["--max-context", "174080"]),
    "180k": ("180K",  ["--max-context", "184320"]),
    "200k": ("200K",  ["--max-context", "204800"]),
    "224k": ("224K",  ["--max-context", "229376"]),
    "256k": ("256K",  ["--max-context", "262144"]),
}
# 投机解码：键 -> (显示名, 参数)。k0=无, k1..k5=MTP, d1..d15=DFlash2
SPEC_OPTIONS = {"k0": ("无", [])}
SPEC_OPTIONS.update({f"k{i}": (f"MTP K={i}", ["--spec", "mtp", "--draft-tokens", str(i)])
                     for i in range(1, 6)})
SPEC_OPTIONS.update({f"d{i}": (f"DFlash2 K={i}",
                               ["--spec", "dflash2", "--draft-tokens", str(i), "--lm-head-draft"])
                     for i in range(1, 16)})
TB_OPTIONS = {
    "none":   ("无(不限)", []),
    "8000":   ("8000",    ["--default-thinking-budget", "8000"]),
    "12000":  ("12000",   ["--default-thinking-budget", "12000"]),
    "16000":  ("16000",   ["--default-thinking-budget", "16000"]),
    "24000":  ("24000",   ["--default-thinking-budget", "24000"]),
    "32000":  ("32000",   ["--default-thinking-budget", "32000"]),
}
# 思考模式开关：off=关闭思考(加 --no-thinking), on=开启(默认，不加参数)
THINK_OPTIONS = {
    "off": ("关闭", ["--no-thinking"]),
    "on":  ("开启", []),
}
# 输出上限：--default-max-tokens（控制思考+输出 token，兼提速）
MAXOUT_OPTIONS = {
    "default": ("默认(65535)", []),
    "1024":    ("1024",     ["--default-max-tokens", "1024"]),
    "4096":    ("4096",     ["--default-max-tokens", "4096"]),
    "8192":    ("8192",     ["--default-max-tokens", "8192"]),
    "16384":   ("16384",    ["--default-max-tokens", "16384"]),
    "32768":   ("32768",    ["--default-max-tokens", "32768"]),
}
# KV 容量预算：--kv-capacity
KVCAP_OPTIONS = {
    "default": ("默认", []),
    "auto":    ("自动(auto)", ["--kv-capacity", "auto"]),
    "16k":     ("16K",  ["--kv-capacity", "16384"]),
    "32k":     ("32K",  ["--kv-capacity", "32768"]),
    "64k":     ("64K",  ["--kv-capacity", "65536"]),
    "128k":    ("128K", ["--kv-capacity", "131072"]),
    "150k":    ("150K", ["--kv-capacity", "153600"]),
    "160k":    ("160K", ["--kv-capacity", "163840"]),
    "170k":    ("170K", ["--kv-capacity", "174080"]),
    "180k":    ("180K", ["--kv-capacity", "184320"]),
    "200k":    ("200K", ["--kv-capacity", "204800"]),
    "224k":    ("224K", ["--kv-capacity", "229376"]),
    "256k":    ("256K", ["--kv-capacity", "262144"]),
}
# 并发度：--max-concurrency（1-8）
CONC_OPTIONS = {
    "1": ("1", []),
    "2": ("2", ["--max-concurrency", "2"]),
    "4": ("4", ["--max-concurrency", "4"]),
    "8": ("8", ["--max-concurrency", "8"]),
}
# 采样预设：封装 temperature/top-p/top-k/greedy 等
SAMPLE_OPTIONS = {
    "default":  ("默认(0.6/0.95)", ["--temperature", "0.6", "--top-p", "0.95"]),
    "stable":   ("稳健(0.5/0.9)",  ["--temperature", "0.5", "--top-p", "0.9"]),
    "topk40":   ("TopK40(0.6/0.95)",["--temperature", "0.6", "--top-p", "0.95", "--top-k", "40"]),
    "creative": ("创意(1.0/0.98)",  ["--temperature", "1.0", "--top-p", "0.98"]),
    "greedy":   ("贪心(greedy)",    ["--greedy"]),
}
# 保留关闭回合推理：--preserve-thinking
PRESERVE_OPTIONS = {
    "off": ("关闭", []),
    "on":  ("开启", ["--preserve-thinking"]),
}
# 视觉（多模态）：--vision 加载视觉塔 + media 子系统
VISION_OPTIONS = {
    "off": ("关闭", []),
    "on":  ("开启", ["--vision"]),
}
# prefill 内核：三选一互斥（引擎派发只走一条，s8 优先于 wide/mma，绝不同时运行）。
#   s8   int8 量化激活后 tensor-core，T>=33 时比 bf16 wide 快 1.2-1.3x（作者实测最快）
#   wide 权重驻留 wide-token-tile
#   mma  原 tensor-core
# 通过环境变量控制（引擎进程级）：NINFER_TERNARY_PREFILL 选 wide/mma；选 s8 时设 NINFER_TERNARY_S8=1。
PREFILL_OPTIONS = {
    "s8":   ("S8(int8·最快)",  {"prefill": None, "s8": "1"}),
    "wide": ("WIDE_T(权重驻留·快)", {"prefill": "wide", "s8": "0"}),
    "mma":  ("MMA(原tensor-core)", {"prefill": "mma", "s8": "0"}),
}

DIMENSIONS = [
    ("model",   "模型",     MODEL_OPTIONS),
    ("think",   "思考模式", THINK_OPTIONS),
    ("tb",      "思考预算", TB_OPTIONS),
    ("maxout",  "输出上限", MAXOUT_OPTIONS),
    ("build",   "构建版本", BUILD_OPTIONS),
    ("kv",      "KV类型",   KV_OPTIONS),
    ("kvcap",   "KV容量",   KVCAP_OPTIONS),
    ("ctx",     "上下文",   CTX_OPTIONS),
    ("spec",    "投机解码", SPEC_OPTIONS),
    ("prefill", "prefill内核", PREFILL_OPTIONS),
    ("vision",  "视觉",     VISION_OPTIONS),
    ("conc",    "并发度",   CONC_OPTIONS),
    ("sample",  "采样",     SAMPLE_OPTIONS),
    ("preserve","保留推理", PRESERVE_OPTIONS),
]

# 默认选中值
DEFAULTS = {"model": "normal", "think": "on", "tb": "none", "maxout": "default", "build": "new", "kv": "k8v4", "kvcap": "default", "ctx": "128k", "spec": "d7", "prefill": "s8", "vision": "off", "conc": "1", "sample": "default", "preserve": "off"}


# ---------------------------------------------------------------
# 配置提示（悬停每个选项显示）与场景预设（一键推荐组合）
# ---------------------------------------------------------------
DIM_TIPS = {
    "model":   "推理模型：正常（Bonsai 三元）或 CRACK（去审查版）。切换后需重启 serve 生效。",
    "think":   "思考模式。开=质量好但生成大量思考、慢；关=直出快但工具编排可能不稳。短任务可关。",
    "tb":      "思考预算上限（每回合最多思考 token）。越小越省时；审核/批量建议小；长逻辑建议大。",
    "maxout":  "单次输出上限（含思考）。限制可防失控浪费；需大于任务实际输出量。",
    "build":   "构建版本：新版(apps) / 旧版(09-22)。",
    "kv":      "KV 缓存精度。k8v4 长上下文省显存；fp8/bf16 精度高但更占显存。",
    "kvcap":   "KV 容量预算。不能小于上下文长度；更小=更省显存更快。",
    "ctx":     "上下文长度。128K 常用；长对话可更大；短文本/审核建议小（快）。",
    "spec":    "投机解码（只加速解码，不影响 prefill）。DFlash2 K=7=速度优先(默认档)：端到端 195~245 tok/s、解码峰值 277~303；MTP K=3=省显存：少占约 1.65 GiB(草稿权重 7.45 vs 9.10 GiB)、接受率更高更稳，但比 DFlash2 慢 5~25%。K 大不一定更快：DFlash2 K>=10 断崖式崩塌(比不开投机还慢 70%+)，MTP K=1~5 吞吐基本持平。长文档档余量紧时选 MTP。",
    "prefill": "prefill 内核（三选一，互斥，绝不同时运行）。S8=int8 量化 tensor-core（T>=33 最快）；WIDE_T=权重驻留；MMA=原 tensor-core。默认 S8。",
    "vision":  "视觉（多模态）：开启后支持图片输入（--vision）。模型内置视觉塔，无需另下文件。",
    "conc":    "并发请求数 1-8。多请求吞吐场景用大值；单会话保持 1。",
    "sample":  "采样预设。默认 0.6/0.95 平衡；贪心最稳；创意更发散。",
    "preserve": "保留关闭回合推理到后续 prompt。多轮工具链/长对话有帮助。",
}
PRESETS = {
    "长对话·默认":  {},
    "快速生成·关思考": {"think": "off"},
    "高质量推理":   {"think": "on", "tb": "24000"},
    "高并发吞吐":   {"think": "off", "conc": "4"},
    "限制·省token": {"maxout": "8192", "tb": "8000"},
}


class ToolTip:
    """极简悬停提示：鼠标悬停任意 widget 显示说明文字，移开/点击即消失。"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self._show, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def _show(self, _e=None):
        if not self.text or self.tip is not None:
            return
        try:
            self.tip = tk.Toplevel(self.widget)
        except Exception:
            self.tip = tk.Toplevel()
        try:
            self.tip.wm_overrideredirect(True)
            self.tip.attributes("-topmost", True)
        except Exception:
            pass
        tk.Label(self.tip, text=self.text, bg="#ffffe4", fg="#222",
                 font=("Microsoft YaHei UI", 9), wraplength=320,
                 justify="left", padx=8, pady=6).pack()
        try:
            x, y = self.widget.winfo_rootx(), self.widget.winfo_rooty()
            h = self.widget.winfo_height()
            self.tip.wm_geometry(f"+{x+24}+{y+h+6}")
        except Exception:
            pass

    def _hide(self, _e=None):
        if self.tip is not None:
            try:
                self.tip.destroy()
            except Exception:
                pass
            self.tip = None


# ---------------------------------------------------------------
# 校验
# ---------------------------------------------------------------
def validate(combo):
    kv = combo.get("kv"); ctx = combo.get("ctx"); spec = combo.get("spec")
    # 224K/256K 长上下文可用 k8v4 或 nvfp4（nvfp4 4bit 更省显存）；fp8/bf16/int8/rk4v4 放不下
    long_ctx_kv_ok = kv in ("k8v4", "nvfp4")
    if ctx == "256k" and not long_ctx_kv_ok:
        return "256K 上下文只支持 k8v4 或 nvfp4（fp8/bf16 显存不够）"
    if ctx == "224k" and not long_ctx_kv_ok:
        return "224K 上下文只支持 k8v4 或 nvfp4"
    if spec.startswith("d"):
        # 224K/256K 显存必须 k8v4 或 nvfp4（bf16 放不下）；DFlash 草案用独立 bf16 小窗口，不受主 KV 影响
        if ctx in ("224k", "256k"):
            if not long_ctx_kv_ok:
                return "DFlash2 + 长上下文只能用 k8v4 或 nvfp4 KV"
        elif ctx == "32k":
            if kv != "bf16":
                return "DFlash2 在 32K 建议用 bf16 KV（中文接受率场景）"
    # KV 容量不能小于上下文长度
    kvcap = combo.get("kvcap", "default")
    if kvcap in ("16k", "32k", "64k", "128k", "150k", "160k", "170k", "180k", "200k", "224k", "256k"):
        ctxval = {"32k": 32768, "128k": 131072, "150k": 153600, "160k": 163840, "170k": 174080, "180k": 184320, "200k": 204800, "224k": 229376, "256k": 262144}.get(ctx, 131072)
        capval = {"16k": 16384, "32k": 32768, "64k": 65536, "128k": 131072, "150k": 153600, "160k": 163840, "170k": 174080, "180k": 184320, "200k": 204800, "224k": 229376, "256k": 262144}[kvcap]
        if capval < ctxval:
            return f"KV容量({kvcap})不能小于上下文长度({ctx}={ctxval})"
    return None


# ---------------------------------------------------------------
# 组合 -> 命令
# ---------------------------------------------------------------
def build_command(combo, port=None):
    port = port or PORT_DEFAULT
    build_val = combo.get("build", "new")
    exe = BUILD_OPTIONS[build_val][1] if build_val in BUILD_OPTIONS else BUILD_OPTIONS["new"][1]
    model_val = combo.get("model", "normal")
    artifact = MODEL_OPTIONS[model_val][1] if model_val in MODEL_OPTIONS else MODEL_OPTIONS["normal"][1]
    cmd = [exe, artifact, "--host", "127.0.0.1", "--port", str(port)]
    cmd.extend(THINK_OPTIONS[combo.get("think", "on")][1])
    tb = combo.get("tb", "none")
    if tb != "none":
        cmd.extend(TB_OPTIONS[tb][1])
    cmd.extend(MAXOUT_OPTIONS[combo.get("maxout", "default")][1])
    cmd.extend(KV_OPTIONS[combo.get("kv", "bf16")][1])
    kvcap = combo.get("kvcap", "default")
    if kvcap != "default":
        cmd.extend(KVCAP_OPTIONS[kvcap][1])
    cmd.extend(CTX_OPTIONS[combo.get("ctx", "32k")][1])
    cmd.extend(SPEC_OPTIONS[combo.get("spec", "k0")][1])
    # 视觉：--vision
    vision = combo.get("vision", "off")
    if vision == "on":
        cmd.extend(VISION_OPTIONS["on"][1])
    # prefill 内核：三选一互斥，环境变量注入（s8 与 wide/mma 不可同开，同一时刻引擎只走一条）
    # prefill 内核：三选一互斥，环境变量注入（s8 与 wide/mma 不可同开，同一时刻引擎只走一条）
    prefill_val = combo.get("prefill", "s8")
    env_prefill = None
    env_s8 = None
    if prefill_val in PREFILL_OPTIONS:
        env_prefill = PREFILL_OPTIONS[prefill_val][1]["prefill"]
        env_s8 = PREFILL_OPTIONS[prefill_val][1]["s8"]
    conc = combo.get("conc", "1")
    if conc != "1":
        cmd.extend(CONC_OPTIONS[conc][1])
    cmd.extend(SAMPLE_OPTIONS[combo.get("sample", "default")][1])
    preserve = combo.get("preserve", "off")
    if preserve == "on":
        cmd.extend(PRESERVE_OPTIONS["on"][1])
    cmd.extend(["--tolerant-tool-calls"])
    return exe, cmd, env_prefill, env_s8


# ---------------------------------------------------------------
# 命名组合（JSON 持久化）
# ---------------------------------------------------------------
def load_profiles():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_profiles(profiles):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(profiles, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------
# 图形界面
# ---------------------------------------------------------------
class LauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NInfer 启动器")
        self.root.geometry("880x680")
        self.root.minsize(760, 640)
        self._left_canvas = None  # 先声明，_build_widgets 里再建
        # 白底淡蓝
        self.bg = "#f4f8ff"
        self.fg = "#1a3a6b"
        self.accent = "#dcebff"
        self.root.configure(bg=self.bg)

        self.profiles = load_profiles()
        self.selection = dict(DEFAULTS)  # 当前选中值
        self._build_widgets()
        self._refresh()

    # ---- 控件 ----
    def _build_widgets(self):
        main = tk.Frame(self.root, bg=self.bg)
        main.pack(fill="both", expand=True, padx=14, pady=12)

        title = tk.Label(main, text="NInfer 启动器", font=("Microsoft YaHei UI", 15, "bold"),
                         bg=self.bg, fg="#1b4d8a")
        title.pack(anchor="w", pady=(0, 4))

        # 左：参数区（带垂直滚动条，保证所有参数组可滚动查看）
        left_outer = tk.Frame(main, bg=self.bg)
        left_outer.pack(side="left", fill="y", padx=(0, 14))
        self._left_canvas = tk.Canvas(left_outer, bg=self.bg, highlightthickness=0, width=180)
        self._left_scroll = ttk.Scrollbar(left_outer, orient="vertical",
                                          command=self._left_canvas.yview)
        self.left_inner = tk.Frame(self._left_canvas, bg=self.bg)
        self.left_inner.bind("<Configure>",
                             lambda e: self._left_canvas.configure(scrollregion=self._left_canvas.bbox("all")))
        self._left_canvas.create_window((0, 0), window=self.left_inner, anchor="nw")
        self._left_canvas.configure(yscrollcommand=self._left_scroll.set)
        self._left_canvas.pack(side="left", fill="y")
        self._left_scroll.pack(side="right", fill="y")
        # 滚轮支持
        self._left_canvas.bind("<Enter>", lambda e: self._left_canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self._left_canvas.bind("<Leave>", lambda e: self._left_canvas.unbind_all("<MouseWheel>"))


        self.var = {}   # 每个维度选中的 tk.StringVar
        self.radios = {}
        self.combos = {}   # 用下拉框的维度（spec）
        self._label2key = {}   # 维度: {显示label: 选项key}
        # 场景预设（一键推荐组合）
        preset_box = tk.LabelFrame(self.left_inner, text="场景预设（推荐）", font=("Microsoft YaHei UI", 10),
                                   bg=self.bg, fg="#2b3a6b")
        preset_box.pack(fill="x", pady=4)
        ToolTip(preset_box, "按场景一键套用推荐组合。选择后自动填充下方参数。")
        self.preset_var = tk.StringVar()
        self.preset_cb = ttk.Combobox(preset_box, state="readonly", textvariable=self.preset_var,
                                      width=20, font=("Microsoft YaHei UI", 9))
        self.preset_cb["values"] = list(PRESETS.keys())
        self.preset_cb.bind("<<ComboboxSelected>>", lambda _e: self._apply_preset())
        self.preset_cb.pack(anchor="w", padx=8, pady=4)
        self.preset_cb.set(list(PRESETS.keys())[0])

        for key, label, opts in DIMENSIONS:
            box = tk.LabelFrame(self.left_inner, text=label, font=("Microsoft YaHei UI", 10),
                                bg=self.bg, fg="#2b3a6b")
            box.pack(fill="x", pady=4)
            ToolTip(box, DIM_TIPS.get(key, ""))
            self.var[key] = tk.StringVar(value=DEFAULTS[key])
            if key == "spec":
                # 投机解码：两级联动下拉 —— 类型（无/MTP/DFlash2）+ K 值
                f = tk.Frame(box, bg=self.bg)
                f.pack(anchor="w", padx=8, pady=4)
                _spec_def = DEFAULTS.get("spec", "d7")
                if _spec_def == "k0":
                    _st, _sk = "无", ""
                elif _spec_def.startswith("k"):
                    _st, _sk = "MTP", _spec_def[1:]
                elif _spec_def.startswith("d"):
                    _st, _sk = "DFlash2", _spec_def[1:]
                else:
                    _st, _sk = "MTP", "2"
                self.var_spec_type = tk.StringVar(value=_st)
                self.var_spec_k = tk.StringVar(value=_sk)
                self.combo_spec_type = ttk.Combobox(f, state="readonly", width=8,
                                                    textvariable=self.var_spec_type)
                self.combo_spec_type["values"] = ["无", "MTP", "DFlash2"]
                self.combo_spec_type.bind("<<ComboboxSelected>>", self._on_spec_change)
                self.combo_spec_type.pack(side="left", padx=(0, 6))
                self.combo_spec_k = ttk.Combobox(f, state="readonly", width=6,
                                                 textvariable=self.var_spec_k)
                self.combo_spec_k.bind("<<ComboboxSelected>>", self._on_spec_change)
                self.combo_spec_k.pack(side="left")
                self._update_spec_k_range()   # 设置 K 下拉范围 + 反映默认值
            else:
                # 下拉菜单（紧凑面板）
                self._label2key[key] = {lbl: val for val, (lbl, _) in opts.items()}
                combo = ttk.Combobox(box, state="readonly", textvariable=self.var[key],
                                     width=20, font=("Microsoft YaHei UI", 9))
                combo["values"] = list(self._label2key[key].keys())
                combo.bind("<<ComboboxSelected>>", lambda _e, k=key: self._on_change())
                combo.pack(anchor="w", padx=8, pady=4)
                dk = DEFAULTS[key]
                combo.set(opts[dk][0] if dk in opts else next(iter(self._label2key[key])))


        # 右：命令预览 + 操作
        right = tk.Frame(main, bg=self.bg)
        right.pack(side="right", fill="both", expand=True)

        tk.Label(right, text="启动命令预览", bg=self.bg, fg="#9b8c5a",
                 font=("Microsoft YaHei UI", 10, "bold")).pack(anchor="w", pady=(0, 2))
        self.cmd_box = tk.Text(right, height=9, width=58, wrap="word",
                               bg="white", fg="#1a1a1a", bd=1, relief="solid",
                               font=("Consolas", 9))
        self.cmd_box.pack(fill="both", expand=True)
        self.cmd_box.configure(state="disabled")

        # 状态行
        self.status = tk.Label(right, text="", bg=self.bg, fg="#4a6b4a",
                               font=("Microsoft YaHei UI", 9))
        self.status.pack(anchor="w", pady=(4, 0))

        # 组合区
        combox = tk.Frame(right, bg=self.bg)
        combox.pack(fill="x", pady=(10, 4))

        tk.Label(combox, text="命名组合:", bg=self.bg, fg="#2b3a6b",
                 font=("Microsoft YaHei UI", 10)).pack(side="left")
        self.profile_cb = ttk.Combobox(combox, state="readonly", width=18,
                                       values=list(self.profiles.keys()))
        self.profile_cb.pack(side="left", padx=(6, 0))
        ttk.Button(combox, text="加载", command=self._load_profile).pack(side="left", padx=4)
        ttk.Button(combox, text="保存当前", command=self._save_profile).pack(side="left", padx=4)
        ttk.Button(combox, text="删除", command=self._del_profile).pack(side="left", padx=4)

        # 启动按钮
        ttk.Button(right, text="启 动", command=self._launch,
                   width=14).pack(pady=(8, 0))

    # ---- 事件 ----
    def _on_mousewheel(self, event):
        self._left_canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def _on_change(self):
        for key, var in self.var.items():
            if key == "spec":
                self.selection["spec"] = self._spec_key_from_ui()
            elif key in self._label2key:
                lbl = var.get()
                self.selection[key] = self._label2key[key].get(lbl, key)
            else:
                self.selection[key] = var.get()
        self._refresh()

    def _apply_preset(self, _e=None):
        """按场景预设一键套用参数组合。"""
        name = self.preset_var.get()
        preset = PRESETS.get(name) or {}
        for key, val in preset.items():
            opts = next(d[2] for d in DIMENSIONS if d[0] == key)
            if val not in opts:
                continue
            if key == "spec":
                if val == "k0":
                    self.var_spec_type.set("无"); self.var_spec_k.set("")
                elif val.startswith("k"):
                    self.var_spec_type.set("MTP"); self.var_spec_k.set(val[1:])
                elif val.startswith("d"):
                    self.var_spec_type.set("DFlash2"); self.var_spec_k.set(val[1:])
                self._update_spec_k_range()
            else:
                self.var[key].set(opts[val][0])
        self._on_change()
        self.status.config(text=f"已应用预设「{name}」", fg="#4a6b4a")

    def _update_spec_k_range(self):
        """按类型更新 K 下拉范围（MTP:1-5, DFlash2:1-15, 无:禁用）。"""
        t = self.var_spec_type.get()
        if t == "无":
            self.combo_spec_k["values"] = []
            self.combo_spec_k.set("")
            self.combo_spec_k.config(state="disabled")
        elif t == "MTP":
            self.combo_spec_k["values"] = [str(i) for i in range(1, 6)]   # 1-5
            self.combo_spec_k.config(state="readonly")
        else:  # DFlash2
            self.combo_spec_k["values"] = [str(i) for i in range(1, 16)]  # 1-15
            self.combo_spec_k.config(state="readonly")
        # 若当前 K 超出范围，重置为范围内的默认
        cur = self.var_spec_k.get()
        if cur not in self.combo_spec_k["values"]:
            self.var_spec_k.set(self.combo_spec_k["values"][0] if self.combo_spec_k["values"] else "")

    def _on_spec_change(self, event=None):
        """投机解码类型或 K 变化时联动。"""
        self._update_spec_k_range()
        self.selection["spec"] = self._spec_key_from_ui()
        self._refresh()

    def _spec_key_from_ui(self):
        """由类型+K 生成 spec 键（k0/k1..k5/d1..d15）。"""
        typ = self.var_spec_type.get()
        k = self.var_spec_k.get()
        if typ == "无":
            return "k0"
        if typ == "MTP":
            return f"k{k}" if k.isdigit() and 1 <= int(k) <= 5 else "k2"
        if typ == "DFlash2":
            return f"d{k}" if k.isdigit() and 1 <= int(k) <= 15 else "d7"
        return "k0"

    def _refresh(self):
        """刷新命令预览 + 校验提示"""
        err = validate(self.selection)
        _, cmd, env_prefill, env_s8 = build_command(self.selection)
        cmdline = " ".join(cmd)
        envs = []
        if env_prefill:
            envs.append(f"NINFER_TERNARY_PREFILL={env_prefill}")
        if env_s8:
            envs.append(f"NINFER_TERNARY_S8={env_s8}")
        if envs:
            cmdline = "[env " + " ".join(envs) + "] " + cmdline
        self.cmd_box.configure(state="normal")
        self.cmd_box.delete("1.0", "end")
        self.cmd_box.insert("1.0", cmdline)
        self.cmd_box.configure(state="disabled")
        if err:
            self.status.config(text="⚠ " + err, fg="#b03030")
        else:
            self.status.config(text="✓ 配置合法，可启动", fg="#4a6b4a")

    def _load_profile(self):
        name = self.profile_cb.get()
        if not name or name not in self.profiles:
            self.status.config(text="未选择或找不到组合", fg="#b03030")
            return
        combo = self.profiles[name]
        valid_keys = {d[0] for d in DIMENSIONS}
        for key, val in combo.items():
            if key not in valid_keys:
                continue
            opts = next(d[2] for d in DIMENSIONS if d[0] == key)
            if val not in opts:
                continue
            if key == "spec":
                # spec 是组合键（k0/k1..k5/d1..d15），反向设置类型+K 两个下拉
                if val == "k0":
                    self.var_spec_type.set("无"); self.var_spec_k.set("")
                elif val.startswith("k"):
                    self.var_spec_type.set("MTP"); self.var_spec_k.set(val[1:])
                elif val.startswith("d"):
                    self.var_spec_type.set("DFlash2"); self.var_spec_k.set(val[1:])
                self._update_spec_k_range()
            else:
                # 写回对应下拉的选中值
                self.var[key].set(opts[val][0])
        # 重建 selection + 刷新预览
        self._on_change()
        self.status.config(text=f"已加载组合 '{name}'", fg="#4a6b4a")


    def _save_profile(self):
        name = tk.simpledialog.askstring("保存组合", "输入组合名称：")
        if not name:
            return
        self.profiles[name] = dict(self.selection)
        save_profiles(self.profiles)
        self.profile_cb["values"] = list(self.profiles.keys())
        self.profile_cb.set(name)
        self.status.config(text=f"已保存组合 '{name}'", fg="#4a6b4a")

    def _del_profile(self):
        name = self.profile_cb.get()
        if not name or name not in self.profiles:
            return
        del self.profiles[name]
        save_profiles(self.profiles)
        self.profile_cb["values"] = list(self.profiles.keys())
        self.profile_cb.set("")

    def _launch(self):
        err = validate(self.selection)
        if err:
            messagebox.showerror("参数不合法", err)
            return
        exe, cmd, env_prefill, env_s8 = build_command(self.selection)
        # 确认框
        if not messagebox.askyesno("启动确认",
                                   f"确认启动 serve？\n\n{exe}\n\n参数:\n{' '.join(cmd)}"):
            return
        env = dict(os.environ)
        env["PATH"] = BUILD_DIR + os.pathsep + env.get("PATH", "")
        if env_prefill:
            env["NINFER_TERNARY_PREFILL"] = env_prefill
        if env_s8:
            env["NINFER_TERNARY_S8"] = env_s8
        # 启动 serve：日志实时显示 + 同时落盘，关闭日志窗口即停 serve
        self._spawn_serve(cmd, env)

    def _spawn_serve(self, cmd, env):
        """启动 serve：真实 CMD 窗口实时显示日志 + 同时落盘到 logs\\serve_<时间戳>.log。
        通过 serve_tee.py 转发；关闭 CMD 窗口 = 停止 serve。
        """
        import time as _time
        ts = _time.strftime("%Y%m%d_%H%M%S")
        logfile = os.path.join(r"J:\Bonsai", "logs", f"serve_{ts}.log")
        tee = os.path.join(r"J:\Bonsai", "serve_tee.py")
        # 用 CREATE_NEW_CONSOLE 启动 serve_tee（真实 CMD 窗口），tee 负责显示+落盘。
        # 用 PYTHON_EXE 而非 sys.executable：GUI 以 pythonw 运行时 sys.executable 指向
        # pythonw.exe（无控制台），会导致日志窗口空白。python.exe 才有控制台输出。
        subprocess.Popen([PYTHON_EXE, tee, logfile] + cmd,
                         env=env, cwd=BUILD_DIR,
                         creationflags=subprocess.CREATE_NEW_CONSOLE)
        self.status.config(text="✓ 已启动（CMD 日志窗口，关闭即停）", fg="#4a6b4a")


def main():
    root = tk.Tk()
    LauncherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()