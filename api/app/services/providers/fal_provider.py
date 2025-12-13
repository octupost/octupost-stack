"""
Fal AI Provider Implementation

This provider handles all Fal AI model integrations using the centralized
model registry for configuration instead of hardcoded if/elif chains.
"""

from typing import Any

import fal_client

from app.registry import Model, Provider, GenerationType
from .base import BaseProvider


# Aspect ratio to dimensions mapping
ASPECT_RATIO_DIMENSIONS: dict[str, tuple[int, int]] = {
    "1:1": (1024, 1024),
    "16:9": (1280, 720),
    "9:16": (720, 1280),
    "21:9": (1344, 576),
    "4:3": (1024, 768),
}


class FalProvider(BaseProvider):
    """
    Provider implementation for Fal AI.
    
    Supports:
    - Text-to-image generation
    - Text-to-video generation
    - Image-to-video generation
    - Text-to-speech generation
    """
    
    async def generate(
        self,
        model_id: str,
        model_config: Model,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute generation using Fal AI.
        
        Args:
            model_id: The model identifier
            model_config: Model configuration from registry
            params: Generation parameters
            
        Returns:
            Normalized result dictionary
        """
        gen_type = model_config.get("type", "")
        provider_config = model_config.get("providerConfig", {})
        
        # Get endpoint
        endpoint = provider_config.get("endpoint", model_id)
        
        # Get mappings and transforms
        param_mapping = provider_config.get("parameterMapping", {})
        param_transforms = provider_config.get("parameterTransforms", {})
        default_params = provider_config.get("defaultParams", {})
        
        # Build input parameters
        input_params = self._build_params(
            params=params,
            gen_type=gen_type,
            param_mapping=param_mapping,
            param_transforms=param_transforms,
            default_params=default_params,
        )
        
        # Handle GPT Image models which require image_size as string
        input_params = self._handle_gpt_image_size(input_params, model_id)
        
        # Call Fal AI API
        result = await fal_client.subscribe_async(
            endpoint,
            arguments=input_params,
        )
        
        # Normalize response
        return self._normalize_response(result, gen_type, params)
    
    def _build_params(
        self,
        params: dict[str, Any],
        gen_type: str,
        param_mapping: dict[str, str],
        param_transforms: dict[str, dict[str, Any]],
        default_params: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Build Fal AI input parameters from standard params.
        
        Args:
            params: Standard input parameters
            gen_type: Generation type
            param_mapping: Parameter name mapping
            param_transforms: Parameter value transforms
            default_params: Default parameters to include
            
        Returns:
            Fal AI formatted parameters
        """
        # Start with defaults
        result = self.merge_defaults(params, default_params)
        
        # Apply transforms (e.g., multiply duration by fps for num_frames)
        result = self.apply_transforms(result, param_transforms)
        
        # Handle aspect ratio to dimensions conversion for images
        if gen_type == "text-to-image":
            result = self._handle_image_dimensions(result)
        
        # Map parameter names
        result = self.map_parameters(result, param_mapping)
        
        return result
    
    def _handle_image_dimensions(self, params: dict[str, Any]) -> dict[str, Any]:
        """
        Handle aspect ratio to dimensions conversion for image generation.
        
        Args:
            params: Input parameters
            
        Returns:
            Parameters with dimensions set
        """
        result = params.copy()
        
        # If aspect_ratio is provided, convert to width/height
        aspect_ratio = result.pop("aspect_ratio", None)
        if aspect_ratio and aspect_ratio in ASPECT_RATIO_DIMENSIONS:
            width, height = ASPECT_RATIO_DIMENSIONS[aspect_ratio]
            result.setdefault("width", width)
            result.setdefault("height", height)
        
        return result
    
    def _handle_gpt_image_size(self, params: dict[str, Any], model_id: str) -> dict[str, Any]:
        """
        Convert image_size from object to string for GPT Image models.
        
        GPT Image models require image_size as a string (e.g., "1024x1024")
        instead of an object with width/height properties.
        
        Args:
            params: Input parameters (after mapping)
            model_id: The model identifier
            
        Returns:
            Parameters with corrected image_size format
        """
        if "gpt-image" not in model_id:
            return params
        
        result = params.copy()
        image_size = result.get("image_size")
        
        if isinstance(image_size, dict):
            width = image_size.get("width", 1024)
            height = image_size.get("height", 1024)
            size_str = f"{width}x{height}"
            
            # GPT Image only accepts specific sizes
            permitted = {"1024x1024", "1536x1024", "1024x1536", "auto"}
            result["image_size"] = size_str if size_str in permitted else "auto"
        
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
        elif gen_type in ("text-to-video", "image-to-video"):
            return self._normalize_video_response(result, original_params)
        elif gen_type == "text-to-speech":
            return self._normalize_speech_response(result, original_params)
        else:
            return result
    
    def _normalize_image_response(
        self,
        result: dict[str, Any],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Normalize image generation response."""
        images = []
        
        for img in result.get("images", []):
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
        
        audio = {
            "url": audio_data.get("url", result.get("audio_url", "")),
            "duration": audio_data.get("duration", 0.0),
            "content_type": audio_data.get("content_type", "audio/wav"),
        }
        
        return {
            "audio": audio,
            "text": params.get("text", params.get("prompt", "")),
            "voice": params.get("voice", ""),
        }


# Singleton instance
fal_provider = FalProvider(provider_config={
    "name": "Fal AI",
    "type": "sdk",
    "sdkPackage": "fal-client",
    "authMethod": "api-key",
    "authEnvVar": "FAL_KEY",
    "baseUrl": None,
    "capabilities": ["text-to-image", "text-to-video", "image-to-video", "text-to-speech"],
    "responseMapping": {},
})

