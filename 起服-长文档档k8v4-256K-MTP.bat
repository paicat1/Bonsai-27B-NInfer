@echo off
rem  Host RAM: pins ~9.2 GiB (host KV 8.0 + host state 1.15); needs
rem    >=~16 GB free RAM or startup fails. Lower via --host-kv-mib / --host-state-slots.
title Ninfer Serve - Agent Dev (k8v4 / FULL 256K ctx / MTP K=2)
rem ============================================================
rem  Agent Dev profile ULTIMATE: k8v4 KV, FULL 262144 ctx,
rem    MTP draft-tokens=2. Tested 2026-09-22:
rem    decode 105.2 tok/s (+55% vs bare 68), VRAM 15.7 GiB.
rem  WARNING: free VRAM only ~0.6 GiB at this profile. Close
rem    other GPU apps first. If a huge prefill ever OOMs mid-task,
rem    fall back to the 224K bat (free ~1.2 GiB, 95.7 tok/s) or
rem    the bare 256K bat (free ~1.1 GiB, 68 tok/s).
rem  MTP acceptance on real agent runs: 59-96%% (typical ~75-80).
rem  Context hygiene: past ~200K quality degrades on ANY long-ctx
rem    scheme - let the agent compress before 200K.
rem  Fallback to SIMT paths (no rebuild): set env before launch
rem    NINFER_TERNARY_PREFILL=block  NINFER_TERNARY_VERIFY=tile
rem  Sampler defaults: temp 0.6 / top-p 0.95; clients can override.
rem  Tool calls: tolerant mode on for agent clients.
rem  Switch profile: close this window, then run the other bat.
rem ============================================================
cd /d J:\Bonsai\landing\repos\ninfer-4090-windows\_build_5080
ninfer-serve.exe J:\Bonsai\landing\artifacts\Ternary-Bonsai-2-27B.ninfer ^
  --host 127.0.0.1 --port 18787 ^
  --max-context 262144 --kv-dtype k8v4 ^
  --spec mtp --draft-tokens 2 ^
  --temperature 0.6 --top-p 0.95 ^
  --tolerant-tool-calls
echo.
echo [serve exited] press any key to close.
pause >nul
