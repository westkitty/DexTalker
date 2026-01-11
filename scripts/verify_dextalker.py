import sys
import os
import asyncio
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
os.chdir(ROOT_DIR)
sys.path.append(str(ROOT_DIR))

from app.engine.chatterbox import ChatterboxEngine

async def verify():
    print("🔍 Starting DexTalker Verification...")
    
    engine = ChatterboxEngine()
    print("✅ Engine instantiated.")
    
    output_dir = Path(engine.get_output_directory())
    print(f"📂 Output directory: {output_dir}")
    
    # Test Synthesis
    text = "Verification test."
    print(f"🗣️ Synthesizing: '{text}'")
    
    path, msg = await engine.synthesize(text)
    
    if path and Path(path).exists() and Path(path).stat().st_size > 0:
        print(f"✅ Success! File created at: {path}")
        print(f"📊 File size: {Path(path).stat().st_size} bytes")
        print("🎉 DexTalker Core is functioning correctly.")
        return 0
    else:
        print(f"❌ Verification Failed. Message: {msg}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(verify())
    sys.exit(exit_code)
