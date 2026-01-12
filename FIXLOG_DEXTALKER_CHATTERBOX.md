# DexTalker Chatterbox Fix Log

## Summary (Symptom + Verification)
- Symptom: UI banner showed `⚠️ **Fallback Mode** (Chatterbox not available)` even though Chatterbox can load in this environment.
- Verification: The banner is produced by `get_engine_status_display()` and was rendered before Chatterbox initialization. This presented a false fallback state at startup.

## Iterations / Changes
1) Initialize Chatterbox on UI load + expose init errors
   - Files: `app/engine/chatterbox.py`, `app/ui/main.py`
   - What changed and why:
     - Added provider error tracking and detailed logging (including a `CHATTERBOX_AVAILABLE=...` line) so underlying failures are visible in logs instead of being swallowed.
     - Added MPS → CPU retry path to avoid false fallback when MPS init fails.
     - UI now shows `Initializing Chatterbox...` at first render and triggers `init_engine_status` on load to initialize the engine and update the banner once ready.
   - How to validate:
     - Start server: `source .venv/bin/activate && python run.py`
     - Confirm banner text is not fallback in initial HTML: `curl -s http://127.0.0.1:7860/ | rg "Fallback Mode|Initializing Chatterbox"`
     - Trigger engine init and confirm status via API:
       - `python - <<'PY'
from gradio_client import Client
client = Client("http://127.0.0.1:7860")
print(client.predict(api_name="/init_engine_status"))
PY`
     - Sanity synth (Chatterbox path):
       - `python - <<'PY'
from gradio_client import Client
client = Client("http://127.0.0.1:7860")
print(client.predict("Hello from DexTalker after fix", "default", False, False, api_name="/synthesize_handler"))
PY`
   - Rollback:
     - `git revert 0f0da1c`

## Validation Results (this run)
- `python run.py` started successfully on `127.0.0.1:7860`.
- Initial HTML contained `Initializing Chatterbox...` and no fallback banner.
- `init_engine_status` returned: `✅ **chatterbox** on mps | 6 voices`.
- Synth call returned a generated WAV path and `✅ Ready: ...` status.
- Logs include `Chatterbox Engine initialized successfully.` and `CHATTERBOX_AVAILABLE=True provider=chatterbox device=mps error=none`.

## Rollback Options
- With git:
  - `git revert 0f0da1c`
- Without git:
  - Restore prior versions of `app/engine/chatterbox.py` and `app/ui/main.py` from backups or VCS.

## Runbook
- Start server:
  - `cd ~/Desktop/Anti_grav/DexTalker && source .venv/bin/activate && python run.py`
- Confirm Chatterbox availability:
  - `python - <<'PY'
from gradio_client import Client
client = Client("http://127.0.0.1:7860")
print(client.predict(api_name="/init_engine_status"))
PY`
- Confirm UI banner is gone:
  - `curl -s http://127.0.0.1:7860/ | rg "Fallback Mode|Initializing Chatterbox"`
- Sanity test (generate speech using Chatterbox):
  - `python - <<'PY'
from gradio_client import Client
client = Client("http://127.0.0.1:7860")
print(client.predict("DexTalker test after fix", "default", False, False, api_name="/synthesize_handler"))
PY`
