"""Inngest functions module - exports all function handlers.

These functions use the unified generation service and model registry
for centralized configuration.
"""

from app.inngest.functions.generate import (
    generate_image_fn,
    generate_video_fn,
    generate_video_from_image_fn,
    generate_speech_fn,
)

# List of all Inngest functions to register
all_functions = [
    generate_image_fn,
    generate_video_fn,
    generate_video_from_image_fn,
    generate_speech_fn,
]

__all__ = [
    "generate_image_fn",
    "generate_video_fn",
    "generate_video_from_image_fn",
    "generate_speech_fn",
    "all_functions",
]
