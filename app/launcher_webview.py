import os
import sys
import subprocess
import socket
import threading
import time
import signal
from pathlib import Path
import webview

# Constants
BASE_DIR = Path(__file__).resolve().parent.parent
PYTHON_EXE = sys.executable

class LauncherAPI:
    def __init__(self, window):
        self.window = window
        self.process = None
        self.desktop_process = None
        self.is_starting = False

    def get_status(self):
        if self.process and self.process.poll() is None:
            return {"status": "Online", "color": "#00ffcc", "url": "http://localhost:7860"}
        return {"status": "Offline", "color": "#ff4b2b", "url": ""}

    def launch_ui(self):
        import webbrowser
        webbrowser.open("http://localhost:7860")
        return True

    def launch_desktop(self):
        if self.desktop_process and self.desktop_process.poll() is None:
            return False
            
        desktop_script = BASE_DIR / "app" / "desktop_app.py"
        self.desktop_process = subprocess.Popen(
            [PYTHON_EXE, str(desktop_script), "--attach"],
            cwd=str(BASE_DIR),
            start_new_session=True
        )
        return True

    def start_engine(self):
        if self.process and self.process.poll() is None:
            return False
            
        self.is_starting = True
        run_script = BASE_DIR / "run.py"
        
        # Kill existing if any
        self.clean_ports()
        
        self.process = subprocess.Popen(
            [PYTHON_EXE, str(run_script)],
            cwd=str(BASE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            start_new_session=True
        )
        
        # Wait for port in a separate check (triggered by UI polling)
        return True

    def clean_ports(self):
        try:
            subprocess.run("lsof -ti:7860 | xargs kill -9", shell=True, stderr=subprocess.DEVNULL)
        except:
            pass

    def shutdown(self):
        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            except:
                pass
        if self.desktop_process:
            try:
                os.killpg(os.getpgid(self.desktop_process.pid), signal.SIGTERM)
            except:
                pass
        self.clean_ports()
        self.window.destroy()
        sys.exit(0)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: #0a0a0f;
            color: #f0f0f5;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
        }
        .container {
            width: 380px;
            padding: 30px;
            background: rgba(18, 18, 26, 0.95);
            border: 1px solid #2a2a35;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        }
        h1 { margin: 0; font-size: 24px; font-weight: 800; }
        .subtitle { color: #00d4ff; font-size: 12px; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 1px; }
        .status-box { 
            background: #12121a; 
            padding: 10px; 
            border-radius: 10px; 
            font-size: 13px; 
            margin-bottom: 25px;
            border: 1px solid rgba(255,255,255,0.05);
        }
        .status-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 8px;
            background: #ff4b2b;
        }
        .status-dot.online { background: #00ffcc; box-shadow: 0 0 10px #00ffcc; }
        
        .button {
            display: block;
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: none;
            border-radius: 12px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-launch { background: #00d4ff; color: #000; }
        .btn-launch:hover { background: #00b8e6; transform: translateY(-2px); }
        .btn-desktop { background: #1a1a25; color: #fff; border: 1px solid #333; }
        .btn-desktop:hover { background: #252535; transform: translateY(-2px); }
        .btn-stop { background: #ff4b2b; color: #fff; margin-top: 20px; font-size: 12px; opacity: 0.8; }
        .btn-stop:hover { opacity: 1; }
        
        .loader {
            display: none;
            width: 20px;
            height: 20px;
            border: 2px solid #f3f3f3;
            border-top: 2px solid #00d4ff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 10px auto;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <h1>DexTalker</h1>
        <div class="subtitle">Chatterbox Engine</div>
        
        <div class="status-box">
            <span id="dot" class="status-dot"></span>
            <span id="status-text">Status: Checking...</span>
        </div>

        <div id="loader" class="loader"></div>
        
        <button class="button btn-launch" onclick="launchUI()">🚀 Launch Web UI</button>
        <button class="button btn-desktop" onclick="launchDesktop()">🖥 Desktop Window</button>
        <button class="button btn-stop" onclick="shutdown()">🛑 Stop Server & Exit</button>
    </div>

    <script>
        async function updateStatus() {
            const result = await pywebview.api.get_status();
            document.getElementById('status-text').innerText = 'Status: ' + result.status;
            const dot = document.getElementById('dot');
            if (result.status === 'Online') {
                dot.className = 'status-dot online';
                document.getElementById('loader').style.display = 'none';
            } else {
                dot.className = 'status-dot';
            }
        }

        function launchUI() { pywebview.api.launch_ui(); }
        function launchDesktop() { pywebview.api.launch_desktop(); }
        function shutdown() { pywebview.api.shutdown(); }

        // Start engine on boot
        window.addEventListener('pywebviewready', () => {
            pywebview.api.start_engine();
            setInterval(updateStatus, 1500);
            document.getElementById('loader').style.display = 'block';
        });
    </script>
</body>
</html>
"""

def main():
    window = webview.create_window(
        'DexTalker Controller', 
        html=HTML, 
        width=420, 
        height=480, 
        resizable=False,
        background_color='#0a0a0f'
    )
    api = LauncherAPI(window)
    window.expose(api)
    webview.start(gui='cocoa')

if __name__ == '__main__':
    main()
