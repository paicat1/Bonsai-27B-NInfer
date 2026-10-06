@echo off
rem  Host RAM: pins ~9.2 GiB (host KV 8.0 + host state 1.15); needs
rem    >=~16 GB free RAM or startup fails. Lower via --host-kv-mib / --host-state-slots.
title Ninfer Serve - Agent Dev v2 (k8v4 / 224K ctx / MTP K=2) [A+B]
rem ============================================================
rem  Agent Dev profile v2: k8v4 KV, 224K ctx, MTP draft-tokens=2
rem  NEW BINARY 20260925: A (CUDA sync switch, default spin) +
rem    B (Q5 split4 band 2..10) merged from upstream. No PPL change
rem    (6.112648 = M5 gold 6.1129) and no decode regression.
rem    (Base params identical to the pre-AB 224K bat.)
rem  Tested 2026-09-22: decode 95.7 tok/s (+40% vs bare 68),
rem    VRAM 15.2 GiB (free ~1.1 GiB, same headroom as the old
rem    256K bare profile). Window trade: -32K ctx for +40% speed.
rem  If you need the FULL 262144 window (rare), close this and
rem    run the old 256K bare bat instead (decode 68).
rem  Fallback to SIMT paths (no rebuild): set env before launch
rem    NINFER_TERNARY_PREFILL=block  NINFER_TERNARY_VERIFY=tile
rem  Context hygiene (KVMem community lessons): past ~200K quality
rem    degrades on ANY long-ctx scheme - let the agent compress
rem    before 200K rather than riding to the ceiling.
rem  Sampler defaults: temp 0.6 / top-p 0.95; clients can override.
rem  Tool calls: tolerant mode on for agent clients.
rem  Switch profile: close this window, then run the other bat.
rem ============================================================
set "NINVER_DIR=J:\Bonsai\landing\repos\ninfer-4090-windows\_build_5080"
set PATH=%NINVER_DIR%;%PATH%
cd /d %NINVER_DIR%\apps
ninfer-serve.exe J:\Bonsai\landing\artifacts\Ternary-Bonsai-2-27B.ninfer ^
  --host 127.0.0.1 --port 18787 ^
  --max-context 224000 --kv-dtype k8v4 ^
  --spec mtp --draft-tokens 2 ^
  --temperature 0.6 --top-p 0.95 ^
  --tolerant-tool-calls
echo.
echo [serve exited] press any key to close.
pause >nul