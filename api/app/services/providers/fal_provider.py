"""
Fal AI Provider Implementation

This provider handles all Fal AI model integrations using the model_configs
database table and the transformer for parameter handling.
"""

from typing import Any

import fal_client

from .base import BaseProvider, Model, Provider
from .transformer import transform_params


# Aspect ratio to dimensions mapping
ASPECT_RATIO_DIMENSIONS: dict[str, tuple[int, int]] = {
    "1:1": (1024, 1024),
    "16:9": (1280, 720),
    "9:16": (720, 1280),
    "21:9": (1344, 576),
    "4:3": (1024, 768),
    "3:2": (1152, 768),
    "2:3": (768, 1152),
    "5:4": (1024, 820),
    "4:5": (820, 1024),
    "3:4": (768, 1024),
}


class FalProvider(BaseProvider):
    """
    Provider implementation for Fal AI.
    
    Supports all generation types defined in provider.json:
    - Text-to-image generation
    - Text-to-video generation  
    - Image-to-video generation
    - Text-to-speech generation
    - Text-to-audio generation
    - Text-to-music generation
    - Video-to-audio generation
    - Avatar generation
    - Reference-to-video generation
    """
    
    async def generate(
        self,
        model_id: str,
        model_config: Model,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute generation using Fal AI.
        
        This method:
        1. Transforms parameters based on provider.json definitions
        2. Handles type conversions (e.g., int to string with "s" suffix)
        3. Maps parameter names to provider-specific names
        4. Calls the Fal AI API
        5. Normalizes the response
        
        Args:
            model_id: The model identifier (endpoint)
            model_config: Model configuration from provider.json
            params: Generation parameters from frontend
            
        Returns:
            Normalized result dictionary
        """
        gen_type = model_config.get("type", "")
        
        # Get endpoint from model config
        endpoint = model_config.get("endpoint", model_id)
        
        # Transform parameters using the new transformer
        # This handles:
        # - Type conversion (int to string, adding "s" suffix, etc.)
        # - Key renaming (duration -> num_frames)
        # - Duration multiplication (* 30 for num_frames)
        # - Merging default_values
        input_params = transform_params(params, model_config)
        
        # Handle special cases
        input_params = self._handle_special_cases(input_params, model_id, gen_type)
        
        # Call Fal AI API
        result = await fal_client.subscribe_async(
            endpoint,
            arguments=input_params,
        )
        
        # Normalize response
        return self._normalize_response(result, gen_type, params)
    
    def _handle_special_cases(
        self,
        params: dict[str, Any],
        model_id: str,
        gen_type: str,
    ) -> dict[str, Any]:
        """
        Handle special parameter cases for specific models.
        
        Args:
            params: Transformed parameters
            model_id: The model identifier
            gen_type: Generation type
            
        Returns:
            Parameters with special cases handled
        """
        result = params.copy()
        
        # Handle GPT Image models - image_size as string
        if "gpt-image" in model_id:
            result = self._handle_gpt_image_size(result)
        
        # Handle aspect ratio to dimensions for some image models
        if gen_type == "text-to-image" and "aspect_ratio" in result:
            result = self._handle_image_dimensions(result)
        
        return result
    
    def _handle_image_dimensions(self, params: dict[str, Any]) -> dict[str, Any]:
        """
        Handle aspect ratio to dimensions conversion for image generation.
        
        Some image models need explicit width/height instead of aspect_ratio.
        
        Args:
            params: Input parameters
            
        Returns:
            Parameters with dimensions set if needed
        """
        result = params.copy()
        
        # If aspect_ratio is provided and no size/width/height, add dimensions
        aspect_ratio = result.get("aspect_ratio")
        if aspect_ratio and aspect_ratio in ASPECT_RATIO_DIMENSIONS:
            if "size" not in result and "width" not in result:
                width, height = ASPECT_RATIO_DIMENSIONS[aspect_ratio]
                result["width"] = width
                result["height"] = height
        
        return result
    
    def _handle_gpt_image_size(self, params: dict[str, Any]) -> dict[str, Any]:
        """
        Convert image_size from object to string for GPT Image models.
        
        GPT Image models require image_size as a string (e.g., "1024x1024")
        instead of an object with width/height properties.
        
        Args:
            params: Input parameters (after mapping)
            
        Returns:
            Parameters with corrected image_size format
        """
        result = params.copy()
        
        # Handle size field mapping for GPT Image
        if "size" in result and isinstance(result["size"], str):
            # Normalize size values
            size = result["size"]
            permitted = {"1024x1024", "1536x1024", "1024x1536", "auto"}
            if size not in permitted:
                # Try to map aspect ratio to size
                aspect_to_size = {
                    "1:1": "1024x1024",
                    "16:9": "1536x1024",
                    "9:16": "1024x1536",
                }
                result["size"] = aspect_to_size.get(size, "auto")
        
        return result
    
    def _normalize_response(
        self,
        result: dict[str, Any],
        gen_type: str,
        original_params: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Normalize Fal AI response to standard format.
        
        Args:
            result: Raw Fal AI response
            gen_type: Generation type
            original_params: Original input parameters
            
        Returns:
            Normalized response dictionary
        """
        if gen_type == "text-to-image":
            return self._normalize_image_response(result, original_params)
        elif gen_type in ("text-to-video", "image-to-video", "reference-to-video", 
                          "first-last-frame-to-video", "avatar", "retake"):
            return self._normalize_video_response(result, original_params)
        elif gen_type in ("text-to-speech",):
            return self._normalize_speech_response(result, original_params)
        elif gen_type in ("text-to-audio", "text-to-music", "video-to-audio"):
            return self._normalize_audio_response(result, original_params)
        else:
            # Return raw result for unknown types
            return result
    
    def _normalize_image_response(
        self,
        result: dict[str, Any],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Normalize image generation response."""
        images = []
        
        # Handle different response formats
        raw_images = result.get("images", [])
        if not raw_images and "image" in result:
            raw_images = [result["image"]]
        
        for img in raw_images:
            if isinstance(img, str):
                # Just a URL
                images.append({
                    "url": img,
                    "width": params.get("width", 1024),
                    "height": params.get("height", 1024),
                    "content_type": "image/png",
                })
            elif isinstance(img, dict):
                images.append({
                    "url": img.get("url", ""),
                    "width": img.get("width", params.get("width", 1024)),
                    "height": img.get("height", params.get("height", 1024)),
                    "content_type": img.get("content_type", "image/png"),
                })
        
        return {
            "images": images,
            "seed": result.get("seed", params.get("seed", 0)),
            "prompt": params.get("prompt", ""),
        }
    
    def _normalize_video_response(
        self,
        result: dict[str, Any],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Normalize video generation response."""
        video_data = result.get("video", {})
        
        # Handle different response formats
        if not video_data and "url" in result:
            video_data = {"url": result["url"]}
        
        # Get dimensions from aspect ratio
        aspect_ratio = params.get("aspect_ratio", "16:9")
        default_width, default_height = ASPECT_RATIO_DIMENSIONS.get(
            aspect_ratio, (1280, 720)
        )
        
        video = {
            "url": video_data.get("url", ""),
            "duration": video_data.get("duration", params.get("duration", 4)),
            "width": video_data.get("width", default_width),
            "height": video_data.get("height", default_height),
            "content_type": video_data.get("content_type", "video/mp4"),
        }
        
        return {
            "video": video,
            "seed": result.get("seed", params.get("seed", 0)),
            "prompt": params.get("prompt", ""),
        }
    
    def _normalize_speech_response(
        self,
        result: dict[str, Any],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Normalize speech generation response."""
        audio_data = result.get("audio", {})
        
        # Handle different response formats
        if not audio_data:
            audio_data = {
                "url": result.get("audio_url", result.get("url", "")),
                "duration": result.get("duration", 0.0),
            }
        
        audio = {
            "url": audio_data.get("url", result.get("audio_url", "")),
            "duration": audio_data.get("duration", 0.0),
            "content_type": audio_data.get("content_type", "audio/wav"),
        }
        
        return {
            "audio": audio,
            "text": params.get("text", params.get("prompt", "")),
            "voice": params.get("voice", params.get("voice_id", "")),
        }
    
    def _normalize_audio_response(
        self,
        result: dict[str, Any],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Normalize audio/music generation response."""
        audio_data = result.get("audio", {})
        
        # Handle different response formats
        if not audio_data:
            audio_data = {
                "url": result.get("audio_url", result.get("url", "")),
                "duration": result.get("duration", params.get("duration", 0.0)),
            }
        
        audio = {
            "url": audio_data.get("url", result.get("audio_url", "")),
            "duration": audio_data.get("duration", params.get("duration", 0.0)),
            "content_type": audio_data.get("content_type", "audio/wav"),
        }
        
        return {
            "audio": audio,
            "prompt": params.get("prompt", ""),
        }


# Singleton instance
fal_provider = FalProvider(provider_config={
    "name": "Fal AI",
    "type": "sdk",
    "sdkPackage": "fal-client",
    "authMethod": "api-key",
    "authEnvVar": "FAL_KEY",
    "baseUrl": None,
    "capabilities": [
        "text-to-image", 
        "text-to-video", 
        "image-to-video", 
        "text-to-speech",
        "text-to-audio",
        "text-to-music",
        "video-to-audio",
        "avatar",
        "reference-to-video",
        "first-last-frame-to-video",
        "retake",
    ],
    "responseMapping": {},
})
