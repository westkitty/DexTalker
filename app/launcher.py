#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
import subprocess
import os
import socket
import signal
import time
import threading
from pathlib import Path
import sys

from launcher_utils import get_configured_port

class DexTalkerLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("DexTalker Controller")
        self.root.geometry("380x280")
        self.root.resizable(False, False)
        self.root.configure(bg="#0a0a0f")
        
        # Paths - Adjusted for DexTalker structure
        # Assumes this script is in DexTalker/app/launcher.py
        self.base_dir = Path(__file__).parent.parent.resolve()
        self.port = get_configured_port(self.base_dir)
        self.run_script = self.base_dir / "run.py"
        self.log_path = self.base_dir / "launcher.log"
        self.log_handle = None
        
        # UI Styling
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TFrame", background="#0a0a0f")
        style.configure("TLabel", background="#0a0a0f", foreground="#f0f0f5", font=("Inter", 12))
        style.configure("Status.TLabel", font=("Inter", 10, "italic"))
        
        # Main Layout
        self.frame = ttk.Frame(self.root, padding="20")
        self.frame.pack(fill="both", expand=True)
        
        self.title_label = ttk.Label(self.frame, text="DexTalker", font=("Inter", 18, "bold"))
        self.title_label.pack(pady=(0, 5))
        
        self.subtitle_label = ttk.Label(self.frame, text="Chatterbox Engine", font=("Inter", 10), foreground="#00d4ff")
        self.subtitle_label.pack(pady=(0, 15))
        
        self.status_label = ttk.Label(self.frame, text="Status: Ready to launch", style="Status.TLabel")
        self.status_label.pack(pady=5)
        
        self.btn_frame = ttk.Frame(self.frame)
        self.btn_frame.pack(pady=20)
        
        self.start_btn = tk.Button(
            self.btn_frame, text="🚀 Launch UI", command=self.open_ui,
            bg="#00d4ff", fg="black", font=("Inter", 11, "bold"),
            padx=15, pady=8, borderwidth=0, cursor="hand2"
        )
        self.start_btn.pack(side="left", padx=10)
        
        self.stop_btn = tk.Button(
            self.btn_frame, text="🛑 Shut Down", command=self.shutdown_and_quit,
            bg="#ff4b2b", fg="white", font=("Inter", 11, "bold"),
            padx=15, pady=8, borderwidth=0, cursor="hand2"
        )
        self.stop_btn.pack(side="left", padx=10)

        self.btn_frame2 = ttk.Frame(self.frame)
        self.btn_frame2.pack(pady=(0, 10))

        self.desktop_btn = tk.Button(
            self.btn_frame2, text="🖥 Desktop Window", command=self.open_desktop_window,
            bg="#7cff6b", fg="black", font=("Inter", 11, "bold"),
            padx=15, pady=8, borderwidth=0, cursor="hand2"
        )
        self.desktop_btn.pack()
        
        # Internal State
        self.process = None
        self.is_running = False
        self.desktop_process = None
        self.desktop_log_handle = None
        
        # Start automatically on launch
        self.launch_thread = threading.Thread(target=self.start_engine, daemon=True)
        self.launch_thread.start()
        
        # Handling window closure
        self.root.protocol("WM_DELETE_WINDOW", self.shutdown_and_quit)

    def _set_status(self, text, color=None):
        def update():
            if color:
                self.status_label.config(text=text, foreground=color)
            else:
                self.status_label.config(text=text)
        self.root.after(0, update)

    def start_engine(self):
        try:
            self.port = get_configured_port(self.base_dir)
            self.clean_ports()
            self.is_running = True
            
            # Start the python run.py script
            # Use the same python interpreter running this launcher
            python_exe = sys.executable
            
            self._set_status("Status: Initializing Chatterbox...")

            try:
                self.log_handle = open(self.log_path, "a")
                stdout_target = self.log_handle
            except OSError:
                self.log_handle = None
                stdout_target = subprocess.DEVNULL
            self.process = subprocess.Popen(
                [python_exe, str(self.run_script)],
                cwd=str(self.base_dir),
                stdout=stdout_target,
                stderr=subprocess.STDOUT,
                start_new_session=True
            )

            if self._wait_for_port("127.0.0.1", self.port, timeout=45):
                self._set_status(f"Status: Online (http://localhost:{self.port})", "#00ffcc")
            else:
                self._set_status("Status: Failed to start (see launcher.log)", "#ff4b2b")
                self.is_running = False
            
        except Exception as e:
            self._set_status(f"Status: Error - {str(e)}", "#ff4b2b")
            self.is_running = False

    def open_ui(self):
        import webbrowser
        webbrowser.open(f"http://localhost:{self.port}")

    def open_desktop_window(self):
        if self.desktop_process and self.desktop_process.poll() is None:
            self.status_label.config(text="Status: Desktop window already open", foreground="#00ffcc")
            return

        try:
            python_exe = sys.executable
            desktop_app = self.base_dir / "app" / "desktop_app.py"
            self.status_label.config(text="Status: Launching desktop window...", foreground="#00ffcc")

            try:
                self.desktop_log_handle = open(self.base_dir / "desktop_window.log", "a")
                stdout_target = self.desktop_log_handle
            except OSError:
                self.desktop_log_handle = None
                stdout_target = subprocess.DEVNULL

            self.desktop_process = subprocess.Popen(
                [python_exe, str(desktop_app), "--attach"],
                cwd=str(self.base_dir),
                stdout=stdout_target,
                stderr=subprocess.STDOUT,
                start_new_session=True
            )
        except Exception as e:
            self.status_label.config(text=f"Status: Desktop window error - {str(e)}", foreground="#ff4b2b")

    def clean_ports(self):
        try:
            subprocess.run(
                f"lsof -ti:{self.port} | xargs kill -9",
                shell=True,
                stderr=subprocess.DEVNULL
            )
        except:
            pass

    def _wait_for_port(self, host, port, timeout=45):
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.process and self.process.poll() is not None:
                return False
            try:
                with socket.create_connection((host, port), timeout=1):
                    return True
            except OSError:
                time.sleep(0.5)
        return False

    def shutdown_and_quit(self):
        self.status_label.config(text="Status: Shutting down...", foreground="#ff4b2b")
        self.root.update()
        
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

        if self.desktop_log_handle:
            try:
                self.desktop_log_handle.close()
            except:
                pass
        
        if self.log_handle:
            try:
                self.log_handle.close()
            except:
                pass
        
        self.clean_ports()
        time.sleep(0.5)
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = DexTalkerLauncher(root)
    root.mainloop()
