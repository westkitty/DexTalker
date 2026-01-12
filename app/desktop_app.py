import argparse
import os
import socket
import threading
import time
from pathlib import Path
import sys
import traceback

BASE_DIR = Path(__file__).resolve().parent.parent
os.chdir(BASE_DIR)
sys.path.append(str(BASE_DIR))

import webview

from app.ui.main import demo
from launcher_utils import get_configured_port


def _port_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False


LOADING_HTML_TEMPLATE = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>DexTalker</title>
    <style>
      :root {
        color-scheme: light;
      }
      body {
        margin: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100vh;
        background: radial-gradient(circle at 20% 20%, #141420, #0a0a0f 60%);
        color: #f0f0f5;
        font-family: "Avenir Next", "Helvetica Neue", Arial, sans-serif;
      }
      .card {
        text-align: center;
        padding: 32px 40px;
        border-radius: 16px;
        background: rgba(18, 18, 26, 0.9);
        border: 1px solid #2a2a35;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
      }
      .title {
        font-size: 22px;
        margin-bottom: 8px;
      }
      .status {
        font-size: 14px;
        opacity: 0.8;
      }
      .dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        margin-left: 6px;
        border-radius: 50%;
        background: #00d4ff;
        animation: pulse 1.2s ease-in-out infinite;
      }
      @keyframes pulse {
        0%, 100% { opacity: 0.3; transform: scale(0.8); }
        50% { opacity: 1; transform: scale(1); }
      }
    </style>
  </head>
  <body>
    <div class="card">
      <div class="title">DexTalker is starting</div>
      <div class="status">Waiting for local server<span class="dot"></span></div>
    </div>
    <script>
      const target = "http://127.0.0.1:{port}";
      async function probe() {
        try {
          const response = await fetch(target, { mode: "no-cors" });
          if (response) {
            window.location.replace(target);
          }
        } catch (e) {
          // keep waiting
        }
      }
      setInterval(probe, 1500);
      probe();
    </script>
  </body>
  </html>
"""


def _find_available_port(start: int, limit: int = 10) -> int:
    for port in range(start, start + limit):
        if not _port_open("127.0.0.1", port):
            return port
    return start


def _launch_gradio(port: int):
    print(f"Starting Gradio server on port {port}...", flush=True)
    
    # Import here to respect network configuration from main.py
    from app.ui.main import demo, network_auth
    
    # Get network configuration
    config = network_auth.get_config()
    bind_addr = config.get("bind_address", "127.0.0.1")
    
    # Desktop app should typically use localhost for security
    # but respect config if network access is enabled
    demo.launch(
        server_name=bind_addr if config.get("lan_enabled") or config.get("tailnet_enabled") else "127.0.0.1",
        server_port=port,
        inbrowser=False,
        prevent_thread_lock=True,
    )

def _parse_args():
    parser = argparse.ArgumentParser(description="DexTalker Desktop Window")
    parser.add_argument(
        "--attach",
        action="store_true",
        help="Only attach to an existing server; do not start one.",
    )
    return parser.parse_args()

def main():
    args = _parse_args()
    started_server = False
    preferred_port = get_configured_port(BASE_DIR)
    port = preferred_port

    if _port_open("127.0.0.1", port):
        if not args.attach:
            port = _find_available_port(preferred_port + 1)
    else:
        if args.attach:
            port = preferred_port

    if not _port_open("127.0.0.1", port):
        if args.attach:
            pass
        else:
            print("No server detected. Launching...", flush=True)
            thread = threading.Thread(target=_launch_gradio, args=(port,), daemon=True)
            thread.start()
            started_server = True

    print(f"Creating webview window for port {port}...", flush=True)
    html = LOADING_HTML_TEMPLATE.replace("{port}", str(port))
    webview.create_window("DexTalker", html=html, width=1200, height=800)
    print("Starting webview...", flush=True)
    webview.start(gui="cocoa", debug=True)
    print("Webview closed.", flush=True)

    if started_server:
        close_fn = getattr(demo, "close", None)
        if callable(close_fn):
            close_fn()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log_dir = Path.home() / "Library" / "Logs" / "DexTalker"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "desktop_app.log"
        with open(log_path, "a") as log_file:
            log_file.write("DexTalker desktop app failed:\n")
            log_file.write(traceback.format_exc())
            log_file.write("\n")

        try:
            import subprocess
            subprocess.run(
                [
                    "osascript",
                    "-e",
                    f'display dialog "DexTalker failed to launch. See {log_path}" with title "DexTalker"',
                ],
                check=False,
            )
        except Exception:
            pass
