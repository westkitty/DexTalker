import gradio as gr
from pathlib import Path
from app.engine.chatterbox import ChatterboxEngine

# Initialize Engine
engine = ChatterboxEngine()

# Starsilk Theme CSS
STARSILK_CSS = """
:root {
    --background: #0a0a0f;
    --surface: #12121a;
    --surface-elevated: #1a1a25;
    --primary: #ff6b00;
    --primary-hover: #ff8533;
    --text-primary: #f0f0f5;
    --text-secondary: #a0a0aa;
    --border: #2a2a35;
    --input-bg: #0f0f15;
}

body, .gradio-container {
    background-color: var(--background) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

.contain {
    background-color: var(--background) !important;
}

.starsilk-panel {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 20px !important;
}

textarea, input {
    background-color: var(--input-bg) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: 8px !important;
}

button.primary {
    background: var(--primary) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
}
button.primary:hover {
    background: var(--primary-hover) !important;
}

footer { display: none !important; }
button[aria-label="Settings"],
button[aria-label="Language"],
#settings-button,
.settings-button {
    display: none !important;
}
"""


def _load_voice_choices():
    return engine.get_available_voices()


def get_engine_status_display():
    """Get formatted engine status for UI display."""
    status = engine.get_engine_status()
    provider = status["provider"]
    device = status["device"]
    fallback = status["fallback_mode"]
    
    if fallback:
        return "⚠️ **Fallback Mode** (Chatterbox not available)"
    else:
        return f"✅ **{provider}** on `{device}` | {status['available_voices_count']} voices"


async def synthesize_handler(text, voice):
    """Generate speech from text."""
    if not text:
        return None, "⚠️ Please enter text to synthesize."

    file_path, status = await engine.synthesize(text, voice)

    if file_path:
        return file_path, f"✅ Ready: {Path(file_path).name}"
    return None, f"❌ {status}"


async def record_voice_handler(duration_sec):
    path, status = await engine.record_voice_sample(duration_sec)
    if path:
        return path, f"✅ {status}"
    return None, f"❌ {status}"


async def add_voice_handler(voice_name, voice_upload, recorded_path):
    source_path = recorded_path or voice_upload
    if not source_path:
        return "❌ Record or upload a voice sample.", gr.update(), gr.update()

    success, msg = await engine.add_voice(voice_name, source_path)
    choices = _load_voice_choices()
    new_value = voice_name if voice_name in choices else (choices[0] if choices else None)
    status_prefix = "✅" if success else "❌"
    return f"{status_prefix} {msg}", gr.update(choices=choices, value=new_value), choices


def refresh_voices_handler():
    choices = _load_voice_choices()
    return gr.update(choices=choices, value=choices[0] if choices else None), choices


with gr.Blocks(css=STARSILK_CSS, title="DexTalker") as demo:
    gr.Markdown("# 🎙️ DexTalker")
    gr.Markdown(get_engine_status_display())

    with gr.Tabs():
        with gr.TabItem("Studio"):
            with gr.Row():
                with gr.Column(elem_classes="starsilk-panel"):
                    gr.Markdown("### Generator")
                    txt_input = gr.Textbox(
                        label="Input Text",
                        lines=5,
                        placeholder="Type here to speak...",
                        value="Welcome to DexTalker. The stars are silent, but we are not."
                    )

                    voice_choices = _load_voice_choices()
                    voice_sel = gr.Dropdown(
                        choices=voice_choices,
                        label="Voice",
                        value=voice_choices[0] if voice_choices else None,
                    )
                    btn_generate = gr.Button("Generate Speech", variant="primary")
                    status_gen = gr.Textbox(label="Status", interactive=False, max_lines=1)
                    audio_gen_out = gr.Audio(label="Generated Output", interactive=False, type="filepath")

        with gr.TabItem("Voices"):
            gr.Markdown("### Record or Upload a Voice Sample")
            gr.Markdown("Recording uses the system microphone; upload works everywhere.")

            with gr.Row():
                with gr.Column(elem_classes="starsilk-panel"):
                    gr.Markdown("#### Record Sample")
                    record_duration = gr.Slider(
                        minimum=2,
                        maximum=20,
                        step=1,
                        value=6,
                        label="Recording Length (seconds)",
                    )
                    btn_record = gr.Button("Record Sample", variant="primary")
                    record_status = gr.Textbox(label="Record Status", interactive=False, max_lines=1)
                    record_preview = gr.Audio(label="Recorded Sample", interactive=False, type="filepath")

                with gr.Column(elem_classes="starsilk-panel"):
                    gr.Markdown("#### Upload Sample")
                    voice_upload = gr.File(label="Voice Sample (.wav)", file_types=[".wav"], type="filepath")

                    gr.Markdown("#### Register Voice")
                    voice_name = gr.Textbox(label="Voice Name", placeholder="e.g. Commander Shepard")
                    btn_add_voice = gr.Button("Register Voice", variant="primary")
                    status_voice = gr.Textbox(label="Status", interactive=False)

            with gr.Row():
                voice_manifest = gr.JSON(value=_load_voice_choices(), label="Available Voices")
                btn_refresh_voices = gr.Button("Refresh Voices")

    btn_generate.click(
        synthesize_handler,
        inputs=[txt_input, voice_sel],
        outputs=[audio_gen_out, status_gen],
    )

    btn_record.click(
        record_voice_handler,
        inputs=[record_duration],
        outputs=[record_preview, record_status],
    )

    btn_add_voice.click(
        add_voice_handler,
        inputs=[voice_name, voice_upload, record_preview],
        outputs=[status_voice, voice_sel, voice_manifest],
    )

    btn_refresh_voices.click(
        refresh_voices_handler,
        outputs=[voice_sel, voice_manifest],
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
