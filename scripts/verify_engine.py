import asyncio
import os
import shutil
from pathlib import Path
from app.engine.chatterbox import ChatterboxEngine

async def test_engine():
    print("--- Starting Engine Verification ---")
    engine = ChatterboxEngine(data_dir="test_data")
    
    # 1. Initialize
    print("1. Initializing...")
    success, msg = await engine.initialize()
    if not success:
        print(f"FAILED: {msg}")
        return
    print(f"PASS: {msg}")
    
    # 2. Synthesize
    print("\n2. Testing Synthesis...")
    path, status = await engine.synthesize("Hello Verification", "default")
    if path and os.path.exists(path):
        print(f"PASS: Generated {path}")
    else:
        print(f"FAILED: {status}")

    # 3. Save Recording
    print("\n3. Testing Save Recording...")
    # Create dummy recording
    dummy_rec = Path("test_rec.wav")
    with open(dummy_rec, "w") as f:
        f.write("dummy audio content")
        
    saved_path, status = await engine.save_recording(str(dummy_rec), "test_rec")
    if saved_path and os.path.exists(saved_path):
        print(f"PASS: Saved to {saved_path}")
    else:
        print(f"FAILED: {status}")
    
    # 4. List Recordings
    print("\n4. Testing List Recordings...")
    recs = engine.get_saved_recordings()
    if len(recs) > 0:
        print(f"PASS: Found {len(recs)} recordings.")
    else:
        print("FAILED: No recordings found.")
        
    # 5. Add Voice
    print("\n5. Testing Add Voice...")
    # Create dummy voice
    dummy_voice = Path("new_voice.wav")
    shutil.copy2(dummy_rec, dummy_voice)
    
    success, msg = await engine.add_voice("New Voice", str(dummy_voice))
    if success:
        print(f"PASS: {msg}")
        voices = engine.get_available_voices()
        if "New Voice" in voices or "new_voice" in voices:
            print(f"PASS: Voice found in list: {voices}")
        else:
            print(f"FAILED: Voice not in list: {voices}")
    else:
        print(f"FAILED: {msg}")

    # Cleanup
    print("\nCleaning up...")
    if os.path.exists("test_data"):
        shutil.rmtree("test_data")
    if os.path.exists("test_rec.wav"):
        os.remove("test_rec.wav")
    if os.path.exists("new_voice.wav"):
        os.remove("new_voice.wav")
    print("--- Verification Complete ---")

if __name__ == "__main__":
    asyncio.run(test_engine())
