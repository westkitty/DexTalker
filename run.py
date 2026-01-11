import os
import sys
from pathlib import Path

def main():
    print("🚀 Starting DexTalker with Chatterbox Engine...")
    
    base_dir = Path(__file__).resolve().parent
    os.chdir(base_dir)
    sys.path.insert(0, str(base_dir))
    
    # Execute main.py which contains the proper launch configuration
    # This ensures network settings are respected
    import runpy
    runpy.run_module("app.ui.main", run_name="__main__")

if __name__ == "__main__":
    main()
