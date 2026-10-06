@echo off
rem  Host RAM: pins ~9.2 GiB (host KV 8.0 + host state 1.15); needs
rem    >=~16 GB free RAM or startup fails. Lower via --host-kv-mib / --host-state-slots.
title Ninfer Serve - Agent Dev v2 (k8v4 / 256K ctx / bare) [A+B]
rem ============================================================
rem  Agent Dev profile v2: k8v4 KV (sm_120a only), FULL 262144 ctx
rem  NEW BINARY 20260925: A (CUDA sync switch, default spin) +
rem    B (Q5 split4 band 2..10) merged from upstream. No PPL change
rem    (6.112648 = M5 gold 6.1129) and no decode regression.
rem    (Base params identical to the pre-AB 256K bare bat.)
rem  Engine: CraneBW kernel merged 20260922 (prefill 2.41x;
rem    T=1 decode GEMV path unchanged -> bare 68 t/s still holds)
rem  Use for: CodeBuddy / DSH / TeleAgent backend, big refactors,
rem    multi-file sessions. 256K ~= 10-20K lines of code + history.
rem  M5.5 verified 2026-09-22: pages 4096/4096, VRAM ~15.4/16.3 GB
rem  NOTE: headroom only ~900 MB - close other GPU apps first.
rem    (MTP/DFlash2 draft heads would NOT fit -> bare decode 68 t/s
rem    is the ceiling for this profile.)
rem    --max-concurrency stays at DEFAULT 1: a 2nd concurrency slot
rem    needs ~1+ GB device state/graph pool -> bad_alloc at CUDA
rem    graph prep on this 256K-full profile (verified 2026-09-22).
rem  If OOM at startup: lower --max-context to 196608 or 131072.
rem  Sampler defaults: temp 0.6 / top-p 0.95; clients can override.
rem  Tool calls: tolerant mode on for agent clients.
rem ============================================================
set "NINVER_DIR=J:\Bonsai\landing\repos\ninfer-4090-windows\_build_5080"
set PATH=%NINVER_DIR%;%PATH%
cd /d %NINVER_DIR%\apps
ninfer-serve.exe J:\Bonsai\landing\artifacts\Ternary-Bonsai-2-27B.ninfer ^
  --host 127.0.0.1 --port 18787 ^
  --max-context 262144 --kv-dtype k8v4 ^
  --temperature 0.6 --top-p 0.95 ^
  --tolerant-tool-calls
echo.
echo [serve exited] press any key to close.
pause >nul