#!/usr/bin/env python3
"""
Simple DexTalker Launcher - No GUI dependencies required
Just starts the server and opens your browser
"""
import os
import sys
import subprocess
import time
import socket
import webbrowser
from pathlib import Path

from launcher_utils import get_configured_port

BASE_DIR = Path(__file__).resolve().parent.parent
PORT = get_configured_port(BASE_DIR)

def check_port(port):
    """Check if server is running on port"""
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=1):
            return True
    except OSError:
        return False

def kill_existing():
    """Kill any existing server on the port"""
    try:
        subprocess.run(f"lsof -ti:{PORT} | xargs kill -9", 
                      shell=True, stderr=subprocess.DEVNULL)
        time.sleep(0.5)
    except:
        pass

def main():
    print("=" * 50)
    print("🚀 DexTalker Launcher")
    print("=" * 50)
    
    # Kill any existing processes
    if check_port(PORT):
        print(f"⚠️  Port {PORT} is in use. Cleaning up...")
        kill_existing()
    
    # Start the server
    print(f"🔧 Starting DexTalker server on port {PORT}...")
    run_script = BASE_DIR / "run.py"
    
    process = subprocess.Popen(
        [sys.executable, str(run_script)],
        cwd=str(BASE_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )
    
    # Wait for server to be ready
    print("⏳ Waiting for server to start", end="", flush=True)
    deadline = time.time() + 45
    while time.time() < deadline:
        if check_port(PORT):
            print(" ✅")
            print(f"\n🎉 DexTalker is online at http://localhost:{PORT}")
            print("\n📋 Features available:")
            print("   • 🎙️  Studio: Text-to-speech generation")
            print("   • 🗣️  Voices: Manage voice profiles")
            print("   • 🎬 Video Voice Clone: Create voices from videos")
            print("   • ⚙️  Network Access: Share over LAN/Tailnet")
            print("\n🌐 Opening browser...")
            time.sleep(1)
            webbrowser.open(f"http://localhost:{PORT}")
            
            print("\n💡 Tip: Keep this window open. Close it to stop the server.")
            print("=" * 50)
            
            try:
                # Keep this script running so user can Ctrl+C to stop
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n🛑 Shutting down DexTalker...")
                kill_existing()
                print("👋 Goodbye!\n")
                sys.exit(0)
        
        print(".", end="", flush=True)
        time.sleep(0.5)
    
    # Timeout
    print(" ❌")
    print("\n⚠️  Server failed to start within 45 seconds")
    print("Check the DexTalker folder for error logs")
    sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
