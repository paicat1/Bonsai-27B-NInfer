@echo off
rem  Host RAM: pins ~9.2 GiB (host KV 8.0 + host state 1.15); needs
rem    >=~16 GB free RAM or startup fails. Lower via --host-kv-mib / --host-state-slots.
title Ninfer Serve - Long-Doc EN (bf16 / 32K ctx / DFlash2 K=7)
rem ============================================================
rem  EN long-form profile: DFlash2 draft-tokens=7 + lm-head-draft
rem  CraneBW merged 20260922, measured (EN, T=0): 139.5 tok/s
rem    (pre-merge 104.7; prefill also 2.41x on this profile)
rem  WARNING: Chinese draft acceptance collapses to 5.4% -> for
rem    English / code tasks only. Daily Chinese tasks use the
rem    daily profile BAT instead.
rem  NOTE: --lm-head-draft is REQUIRED: default Full-head path
rem    fails at startup (linear_topk head profile mismatch).
rem  VRAM budget: weights 9.1G + KV 2.5G + runtime ~= 13G
rem  Switch profile: close this window, then run the other bat.
rem ============================================================
cd /d J:\Bonsai\landing\repos\ninfer-4090-windows\_build_5080
ninfer-serve.exe J:\Bonsai\landing\artifacts\Ternary-Bonsai-2-27B.ninfer ^
  --host 127.0.0.1 --port 18787 ^
  --max-context 32768 --kv-dtype bf16 ^
  --spec dflash2 --draft-tokens 7 --lm-head-draft ^
  --temperature 0.6 --top-p 0.95 ^
  --tolerant-tool-calls
rem  (no --max-concurrency: free ~2.6 GiB only, 2nd slot risks OOM)
echo.
echo [serve exited] press any key to close.
pause >nul
