@echo off
rem  Host RAM: pins ~9.2 GiB (host KV 8.0 + host state 1.15); needs
rem    >=~16 GB free RAM or startup fails. Lower via --host-kv-mib / --host-state-slots.
title Ninfer Serve - Agent Dev TB16K (k8v4 / FULL 256K ctx / MTP K=2)
rem ============================================================
rem  Agent Dev profile: k8v4 KV, FULL 262144 ctx, MTP draft-tokens=2
rem    + THINKING BUDGET independent cap (default 16000).
rem  PURPOSE: stop the "xhigh thinking wall" dead loop. Without a
rem    budget, xhigh thinking can burn the whole 65,536 max output
rem    and produce zero body, then "continue" rebuilds from scratch
rem    forever. Setting --default-thinking-budget N forces the model
rem    to stop thinking at N tokens and start the body with the
rem    remaining output budget.
rem  MECHANISM (engine source): model_token_budget_remaining()
rem    returns 0 once thinking_tokens >= budget, forcing the
rem    reasoning phase to close and body to begin.
rem  BUDGET TRADE-OFF: max output = 65,536, body room = 65,536 - N.
rem    N=16000 => body ~49K (recommended). 8000=>57K, 24000=>41K.
rem  SCOPE WARNING: only serves started from THIS bat carry the
rem    budget. The other 10 bats are unchanged. BUT a client that
rem    sends its own thinking_budget field overrides this default
rem    (request wins over server default). Verify your agent client.
rem  WARNING: free VRAM only ~0.6 GiB at this profile. Close other
rem    GPU apps first. Fall back to 224K if OOM.
rem  MTP K=2 (draft-tokens 2); temp 0.6 / top-p 0.95.
rem ============================================================
set "NINVER_DIR=J:\Bonsai\landing\repos\ninfer-4090-windows\_build_5080"
set PATH=%NINVER_DIR%;%PATH%
cd /d %NINVER_DIR%\apps
ninfer-serve.exe J:\Bonsai\landing\artifacts\Ternary-Bonsai-2-27B.ninfer ^
  --host 127.0.0.1 --port 18787 ^
  --max-context 262144 --kv-dtype k8v4 ^
  --spec mtp --draft-tokens 2 ^
  --default-thinking-budget 16000 ^
  --temperature 0.6 --top-p 0.95 ^
  --tolerant-tool-calls
echo.
echo [serve exited] press any key to close.
pause >nul