@echo off
rem  Host RAM: pins ~9.2 GiB (host KV 8.0 + host state 1.15); needs
rem    >=~16 GB free RAM or startup fails. Lower via --host-kv-mib / --host-state-slots.
title Ninfer Serve - Daily v2 (fp8 KV / 32K ctx / MTP K=2) [A+B]
rem ============================================================
rem  Daily profile v2: fp8 KV, 32K context, MTP draft-tokens=2
rem  NEW BINARY 20260925: A (CUDA sync switch, default spin) +
rem    B (Q5 split4 band 2..9) merged from upstream. No PPL change
rem    (6.112648 = M5 gold 6.1129) and no decode regression
rem    (bf16 K2 ~118 t/s, same as pre-merge flat).
rem  Base params identical to the pre-AB daily bat:
rem  Engine: CraneBW kernel merged 20260922 (PPL 6.1126 = M5 gold
rem    6.1129, 0.005%; prefill 2.41x; verify small-T tensor core)
rem  fp8 KV: half the KV memory; long-context ceiling bf16 ~120K
rem    -> fp8 ~238K (CraneBW measured 6/6 needle recall @192k fp8).
rem  VRAM: ~10.2 GiB with concurrency 2 (free ~6 GiB, verified).
rem  Rollback to SIMT paths (no rebuild): set env before launch
rem    NINFER_TERNARY_PREFILL=block  NINFER_TERNARY_VERIFY=tile
rem  Sampler defaults: temp 0.6 / top-p 0.95 (Qwen3 thinking rec.);
rem    clients can override per-request.
rem  Thinking: ON by default (template default = xhigh). Clients may
rem    set reasoning_effort per request. To disable globally add
rem    --no-thinking  (NOTE: requests then carrying reasoning_effort
rem    will get 400 from the template layer).
rem  Tool calls: tolerant mode on for agent clients.
rem  Switch profile: close this window, then run the other bat.
rem ============================================================
set "NINVER_DIR=J:\Bonsai\landing\repos\ninfer-4090-windows\_build_5080"
set PATH=%NINVER_DIR%;%PATH%
cd /d %NINVER_DIR%\apps
ninfer-serve.exe J:\Bonsai\landing\artifacts\Ternary-Bonsai-2-27B.ninfer ^
  --host 127.0.0.1 --port 18787 ^
  --max-context 32768 --kv-dtype fp8 ^
  --spec mtp --draft-tokens 2 ^
  --temperature 0.6 --top-p 0.95 ^
  --tolerant-tool-calls ^
  --max-concurrency 2
rem  (concurrency 2 verified 20260922 on fp8+K=2: dual-stream OK)
echo.
echo [serve exited] press any key to close.
pause >nul