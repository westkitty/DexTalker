# DexTalker Launch Icon + Brave Fix Log

## What Was Broken
- Clicking the “Launch DexTalker” icon caused a dock flicker then exit. The app reported:
  - `Can't get container of alias "Macintosh HD:Users:andrew:Desktop:Anti_grav:DexTalker:Launch DexTalker.app". (-1728)`
- Brave was not opening automatically.

## Changes
1) Reliable launcher script (server + readiness + Brave + stay alive)
   - File: `Launch_DexTalker.command`
   - What/why:
     - Activates the venv, starts `python run.py`, waits for HTTP readiness, opens Brave in a new window, then blocks on the server PID so the Terminal session stays alive.
     - Writes server logs to `~/Library/Logs/DexTalker/launcher_icon.log` for visibility.
   - Validation:
     - `./Launch_DexTalker.command` (dry run)
     - `curl -fsS http://127.0.0.1:7860/`
     - Brave opens a new window to the URL after readiness.
   - Rollback:
     - `git revert <commit>` (see below)

2) Fix app alias/container error + log app launches
   - File: `Launch DexTalker.app` (AppleScript app bundle)
   - What/why:
     - Avoids `container of (path to me)` and instead uses `dirname` on the app path to locate the repo reliably.
     - Adds a small log at `~/Library/Logs/DexTalker/launcher_app.log` to confirm icon launches and Terminal automation success/failure.
   - Validation:
     - Double-click `Launch DexTalker.app` in Finder (or `open` it) and confirm:
       - Terminal launches and stays open
       - Server is listening on 127.0.0.1:7860
       - Brave opens a new window to the URL
   - Rollback:
     - `git revert <commit>` (see below)

## Validation Results (this run)
- Finder-equivalent open: `open "/Users/andrew/Desktop/Anti_grav/DexTalker/Launch DexTalker.app"`
- Log shows app launched and resolved repo path:
  - `~/Library/Logs/DexTalker/launcher_app.log`
- Server came up and stayed running > 60 seconds:
  - `lsof -nP -iTCP:7860 -sTCP:LISTEN`
  - `ps -p <pid>` (after 60 seconds)
- HTTP ready check passed:
  - `curl -fsS http://127.0.0.1:7860/`

## Rollback Options
- With git:
  - `git revert <commit>` for each change (see `git log --oneline` on branch `fix/launcher-brave`)
- Without git:
  - Restore `Launch_DexTalker.command` and `Launch DexTalker.app` from backups or a prior snapshot

## Runbook
- Click icon: `Launch DexTalker.app` (Finder)
- Server should listen:
  - `lsof -nP -iTCP:7860 -sTCP:LISTEN`
- Check UI:
  - `curl -fsS http://127.0.0.1:7860/`
- Manual Brave open (if needed):
  - `open -na "Brave Browser" --args --new-window http://127.0.0.1:7860`
