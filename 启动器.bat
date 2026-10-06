@echo off
rem  Host RAM: pins ~9.2 GiB (host KV 8.0 + host state 1.15); needs
rem    >=~16 GB free RAM or startup fails. Lower via --host-kv-mib / --host-state-slots.
rem ============================================================
rem  NInfer launcher. Double-click to open the GUI.
rem  Uses `start` so the bat's CMD window closes immediately
rem  (no blank window lingers). Serve connects via its own port.
rem ============================================================
start "NInfer-Launcher" "D:\Python311\pythonw.exe" "J:\Bonsai\ninfer_launcher.py"