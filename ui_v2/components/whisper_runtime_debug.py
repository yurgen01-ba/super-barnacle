from __future__ import annotations

import streamlit as st

from transcription.runtime_diagnostics import get_whisper_runtime_diagnostics


def render_whisper_runtime_debug():
    runtime = get_whisper_runtime_diagnostics()

    with st.expander("Whisper Runtime Debug", expanded=False):
        st.code(
            "\n".join(
                [
                    f"Whisper model: {runtime.get('whisper_model')}",
                    f"Requested device: {runtime.get('requested_device')}",
                    f"Actual device: {runtime.get('actual_device')}",
                    f"CUDA available: {runtime.get('cuda_available')}",
                    f"GPU: {runtime.get('gpu_name')}",
                    f"FP16 requested: {runtime.get('fp16_requested')}",
                    f"FP16 effective: {runtime.get('fp16_effective')}",
                    f"Beam size: {runtime.get('beam_size')}",
                    f"Best of: {runtime.get('best_of')}",
                    f"Torch: {runtime.get('torch_version')}",
                    f"Torch CUDA runtime: {runtime.get('torch_cuda_runtime')}",
                ]
            )
        )

        if runtime.get("warning"):
            st.error(runtime["warning"])
