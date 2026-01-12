# DexTalker Launch Stability Fix Log

## Summary
- Observed error: `OSError: Cannot find empty port in range: 7860-7860` at `app/ui/main.py` when `demo.launch(server_name=bind_addr, server_port=port)` attempted to bind on an occupied port.
- Runtime behavior also printed shareable LAN/Tailscale URLs even when the server bound only to `127.0.0.1`, which was misleading.

## Changes
1) Port and host resolution + truthful URL generation
   - Files: `app/ui/main.py`, `app/network/utils.py`
   - What/why:
     - Added deterministic host/port selection with env overrides (`GRADIO_SERVER_NAME`/`GRADIO_SERVER_HOST`, `GRADIO_SERVER_PORT`, `DEXTALKER_PORT_RANGE`, `ALLOW_PORT_FALLBACK`, `DEXTALKER_BIND_ALL`) so launch never fails when 7860 is occupied unless an explicit port is forced.
     - Added port availability checks, range scan, and OS-assigned fallback port.
     - Updated shareable URL generation to include LAN/Tailscale only when bound to `0.0.0.0` (bind-all), and updated UI text to avoid claiming reachability otherwise.
     - Logging now reports the actual bind host and selected port.
   - How to validate:
     - `source .venv/bin/activate && python run.py` (free port -> 7860)
     - `GRADIO_SERVER_PORT=7860 python run.py` with 7860 occupied -> clean failure message
     - `DEXTALKER_BIND_ALL=1 python run.py` -> bind `0.0.0.0` and LAN/Tailscale URLs populated
   - Rollback:
     - `git revert ec45afb`

2) Launch script uses venv + run.py
   - File: `Launch_DexTalker.command`
   - What/why:
     - Activates `.venv` (or `.venv311`) when present and runs `python run.py` directly, matching the supported launch path and allowing optional `DEXTALKER_BIND_ALL=1` for share mode.
   - How to validate:
     - Double-click `Launch_DexTalker.command` or run it from Terminal.
   - Rollback:
     - `git revert 503b861`

## Validation Results
- Scenario 1 (port 7860 free): started on `127.0.0.1:7860`, UI returned HTTP 200 at `http://127.0.0.1:7860/`.
- Scenario 2 (port 7860 occupied): started on `127.0.0.1:7861`, UI returned HTTP 200 at `http://127.0.0.1:7861/`.
- Scenario 3 (`GRADIO_SERVER_PORT=7860` occupied): exited with message `Port 7860 is already in use on 127.0.0.1. Set ALLOW_PORT_FALLBACK=1 to choose another port.`
- Scenario 4 (`DEXTALKER_BIND_ALL=1`): bound to `0.0.0.0` and logged LAN/Tailscale/MagicDNS URLs.
- Scenario 5 (UI loads): HTTP 200 verified via `curl` for each run.

## Rollback Options
- With git:
  - `git revert ec45afb`
  - `git revert 503b861`
- Without git:
  - Restore the previous file versions from backups (if available) or from your VCS snapshot.

## Runbook
- Local-only run:
  - `source .venv/bin/activate && python run.py`
- Share-mode run:
  - `source .venv/bin/activate && DEXTALKER_BIND_ALL=1 python run.py`
- Check port listeners:
  - `lsof -nP -iTCP:<port> -sTCP:LISTEN`
- Confirm UI responds:
  - `curl http://127.0.0.1:<port>/`
