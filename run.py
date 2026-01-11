import os
import sys
from pathlib import Path

def main():
    print("🚀 Starting DexTalker with Chatterbox Engine...")
    
    base_dir = Path(__file__).resolve().parent
    os.chdir(base_dir)
    sys.path.append(str(base_dir))
    
    # We can run the Gradio app directly or via uvicorn if we mount it
    # For simplicity in this new architecture, we'll run the Gradio launch directly
    # but wrapped in a clean function
    
    from app.ui.main import demo
    demo.launch(server_name="127.0.0.1", server_port=7860)

if __name__ == "__main__":
    main()
