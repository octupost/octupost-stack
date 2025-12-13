"""Fal AI client service for media generation."""

from typing import Any, Optional

import fal_client

from app.models.schemas import (
    AspectRatio,
    ImageModel,
    ImageResult,
    ImageToVideoModel,
    TextToImageRequest,
    TextToImageResult,
    TextToSpeechRequest,
    TextToSpeechResult,
    TextToVideoRequest,
    TextToVideoResult,
    TTSModel,
    VideoModel,
    VideoResult,
    AudioResult,
    ImageToVideoRequest,
    ImageToVideoResult,
)


# =============================================================================
# Model Configuration
# =============================================================================

# Mapping of aspect ratios to dimensions
ASPECT_RATIO_DIMENSIONS = {
    AspectRatio.SQUARE: (1024, 1024),
    AspectRatio.LANDSCAPE: (1280, 720),
    AspectRatio.PORTRAIT: (720, 1280),
    AspectRatio.WIDE: (1344, 576),
    AspectRatio.STANDARD: (1024, 768),
}


class FalClient:
    """Client for interacting with Fal AI APIs."""

    # =========================================================================
    # Text-to-Image Generation
    # =========================================================================

    async def generate_image(self, request: TextToImageRequest) -> TextToImageResult:
        """
        Generate images from text using Fal AI.

        Args:
            request: Text-to-image generation request

        Returns:
            TextToImageResult with generated images
        """
        # Determine dimensions
        if request.aspect_ratio:
            width, height = ASPECT_RATIO_DIMENSIONS.get(
                request.aspect_ratio, (request.width, request.height)
            )
        else:
            width, height = request.width, request.height

        # Build input parameters based on model
        input_params: dict[str, Any] = {
            "prompt": request.prompt,
            "image_size": {"width": width, "height": height},
            "num_images": request.num_images,
        }

        # Add optional parameters
        if request.negative_prompt:
            input_params["negative_prompt"] = request.negative_prompt
        if request.seed is not None:
            input_params["seed"] = request.seed

        # Model-specific parameters
        if request.model == ImageModel.GPT_IMAGE_1_MINI:
            # GPT Image 1 Mini uses standard parameters
            input_params["guidance_scale"] = request.guidance_scale
            input_params["num_inference_steps"] = request.num_inference_steps
        elif request.model == ImageModel.FLUX_SCHNELL:
            input_params["num_inference_steps"] = min(request.num_inference_steps, 4)
        elif request.model == ImageModel.FAST_SDXL:
            input_params["guidance_scale"] = request.guidance_scale
            input_params["num_inference_steps"] = request.num_inference_steps

        # Call Fal AI API
        result = await fal_client.subscribe_async(
            request.model.value,
            arguments=input_params,
        )

        # Parse response
        images = []
        for img in result.get("images", []):
            images.append(
                ImageResult(
                    url=img.get("url", ""),
                    width=img.get("width", width),
                    height=img.get("height", height),
                    content_type=img.get("content_type", "image/png"),
                )
            )

        return TextToImageResult(
            images=images,
            seed=result.get("seed", request.seed or 0),
            prompt=request.prompt,
        )

    # =========================================================================
    # Text-to-Video Generation
    # =========================================================================

    async def generate_video(self, request: TextToVideoRequest) -> TextToVideoResult:
        """
        Generate video from text using Fal AI.

        Args:
            request: Text-to-video generation request

        Returns:
            TextToVideoResult with generated video
        """
        # Get dimensions from aspect ratio
        width, height = ASPECT_RATIO_DIMENSIONS.get(
            request.aspect_ratio, (1280, 720)
        )

        input_params: dict[str, Any] = {
            "prompt": request.prompt,
        }

        # Model-specific parameters
        if request.model == VideoModel.INFINITY_STAR:
            # Infinity Star model parameters
            input_params["aspect_ratio"] = request.aspect_ratio.value
            if request.negative_prompt:
                input_params["negative_prompt"] = request.negative_prompt
            if request.seed is not None:
                input_params["seed"] = request.seed

        elif request.model == VideoModel.WAN_T2V:
            input_params["aspect_ratio"] = (
                "16:9" if request.aspect_ratio == AspectRatio.LANDSCAPE else "9:16"
            )
            input_params["num_inference_steps"] = request.num_inference_steps
            input_params["guidance_scale"] = request.guidance_scale
            if request.negative_prompt:
                input_params["negative_prompt"] = request.negative_prompt
            if request.seed is not None:
                input_params["seed"] = request.seed

        elif request.model == VideoModel.MINIMAX:
            input_params["prompt_optimizer"] = True
            if request.negative_prompt:
                input_params["negative_prompt"] = request.negative_prompt

        elif request.model == VideoModel.LUMA_DREAM:
            input_params["aspect_ratio"] = request.aspect_ratio.value
            if request.seed is not None:
                input_params["seed"] = request.seed

        elif request.model == VideoModel.LONGCAT_DISTILLED:
            # LongCat Video Distilled parameters
            # num_frames at 15fps: 4s = 60 frames, 8s = 120 frames
            input_params["num_frames"] = request.duration * 15
            if request.seed is not None:
                input_params["seed"] = request.seed

        # Call Fal AI API
        result = await fal_client.subscribe_async(
            request.model.value,
            arguments=input_params,
        )

        # Parse response
        video_data = result.get("video", {})
        video = VideoResult(
            url=video_data.get("url", ""),
            duration=video_data.get("duration", request.duration),
            width=video_data.get("width", width),
            height=video_data.get("height", height),
            content_type=video_data.get("content_type", "video/mp4"),
        )

        return TextToVideoResult(
            video=video,
            seed=result.get("seed", request.seed or 0),
            prompt=request.prompt,
        )

    # =========================================================================
    # Image-to-Video Generation
    # =========================================================================

    async def generate_video_from_image(
        self, request: ImageToVideoRequest
    ) -> ImageToVideoResult:
        """
        Generate video from an image using Fal AI.

        Args:
            request: Image-to-video generation request

        Returns:
            ImageToVideoResult with generated video
        """
        input_params: dict[str, Any] = {
            "image_url": request.image_url,
            "prompt": request.prompt,
        }

        # Model-specific parameters
        if request.model == ImageToVideoModel.MINIMAX_I2V:
            input_params["prompt_optimizer"] = True
            if request.negative_prompt:
                input_params["negative_prompt"] = request.negative_prompt

        elif request.model == ImageToVideoModel.LUMA_DREAM:
            input_params["aspect_ratio"] = "16:9"
            if request.seed is not None:
                input_params["seed"] = request.seed

        # Call Fal AI API
        result = await fal_client.subscribe_async(
            request.model.value,
            arguments=input_params,
        )

        # Parse response
        video_data = result.get("video", {})
        video = VideoResult(
            url=video_data.get("url", ""),
            duration=video_data.get("duration", request.duration),
            width=video_data.get("width", 1280),
            height=video_data.get("height", 720),
            content_type=video_data.get("content_type", "video/mp4"),
        )

        return ImageToVideoResult(
            video=video,
            seed=result.get("seed", request.seed or 0),
            source_image=request.image_url,
        )

    # =========================================================================
    # Text-to-Speech Generation
    # =========================================================================

    async def generate_speech(self, request: TextToSpeechRequest) -> TextToSpeechResult:
        """
        Generate speech from text using Fal AI.

        Args:
            request: Text-to-speech generation request

        Returns:
            TextToSpeechResult with generated audio
        """
        input_params: dict[str, Any] = {
            "prompt": request.text,
            "voice": request.voice.value,
            "speed": request.speed,
        }

        # Model-specific adjustments
        if request.model == TTSModel.F5_TTS:
            # F5-TTS has slightly different parameter names
            input_params["gen_text"] = request.text
            del input_params["prompt"]

        # Call Fal AI API
        result = await fal_client.subscribe_async(
            request.model.value,
            arguments=input_params,
        )

        # Parse response
        audio_data = result.get("audio", {})
        audio = AudioResult(
            url=audio_data.get("url", result.get("audio_url", "")),
            duration=audio_data.get("duration", 0.0),
            content_type=audio_data.get("content_type", "audio/wav"),
        )

        return TextToSpeechResult(
            audio=audio,
            text=request.text,
            voice=request.voice.value,
        )


# Create singleton instance
fal_service = FalClient()

