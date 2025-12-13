"""
Unified Generation Service

This service provides a single entry point for all AI generation requests,
routing to the appropriate provider based on the model's configuration.
"""

from typing import Any, Optional, Type

from app.registry import (
    get_model,
    get_provider,
    is_valid_model,
    validate_params,
    GenerationType,
)
from .providers.base import BaseProvider
from .providers.fal_provider import FalProvider


# Provider registry mapping provider IDs to their implementations
PROVIDER_HANDLERS: dict[str, Type[BaseProvider]] = {
    "fal-ai": FalProvider,
    # Future providers:
    # "runway": RunwayProvider,
    # "elevenlabs": ElevenLabsProvider,
    # "openai": OpenAIProvider,
}


class GenerationService:
    """
    Unified service for AI generation requests.
    
    Routes requests to the appropriate provider based on the model's
    configuration in the registry.
    
    Example:
        service = GenerationService()
        result = await service.generate(
            model_id="fal-ai/flux/schnell",
            params={"prompt": "A beautiful sunset"}
        )
    """
    
    def __init__(self):
        """Initialize the generation service."""
        self._provider_instances: dict[str, BaseProvider] = {}
    
    def _get_provider_instance(self, provider_id: str) -> Optional[BaseProvider]:
        """
        Get or create a provider instance.
        
        Args:
            provider_id: The provider identifier
            
        Returns:
            Provider instance or None if not found
        """
        if provider_id in self._provider_instances:
            return self._provider_instances[provider_id]
        
        provider_class = PROVIDER_HANDLERS.get(provider_id)
        if not provider_class:
            return None
        
        provider_config = get_provider(provider_id)
        if not provider_config:
            return None
        
        instance = provider_class(provider_config)
        self._provider_instances[provider_id] = instance
        return instance
    
    async def generate(
        self,
        model_id: str,
        params: dict[str, Any],
        validate: bool = True,
    ) -> dict[str, Any]:
        """
        Execute a generation request.
        
        Args:
            model_id: The model identifier (e.g., "fal-ai/flux/schnell")
            params: Generation parameters
            validate: Whether to validate parameters before generation
            
        Returns:
            Normalized generation result
            
        Raises:
            ValueError: If model is invalid or provider not implemented
        """
        # Get model configuration
        model_config = get_model(model_id)
        if not model_config:
            raise ValueError(f"Unknown model: {model_id}")
        
        if not model_config.get("enabled", False):
            raise ValueError(f"Model {model_id} is not enabled")
        
        # Validate parameters
        if validate:
            validation = validate_params(model_id, params)
            if not validation["valid"]:
                raise ValueError(f"Invalid parameters: {', '.join(validation['errors'])}")
        
        # Get provider
        provider_id = model_config.get("provider", "")
        provider = self._get_provider_instance(provider_id)
        
        if not provider:
            raise ValueError(f"Provider not implemented: {provider_id}")
        
        # Execute generation
        return await provider.generate(model_id, model_config, params)
    
    async def generate_image(
        self,
        model_id: str,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        num_images: int = 1,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Convenience method for image generation.
        
        Args:
            model_id: The image model identifier
            prompt: Text prompt for generation
            width: Image width in pixels
            height: Image height in pixels
            num_images: Number of images to generate
            **kwargs: Additional parameters
            
        Returns:
            Generation result with images
        """
        params = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "num_images": num_images,
            **kwargs,
        }
        return await self.generate(model_id, params)
    
    async def generate_video(
        self,
        model_id: str,
        prompt: str,
        aspect_ratio: str = "16:9",
        duration: int = 4,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Convenience method for video generation.
        
        Args:
            model_id: The video model identifier
            prompt: Text prompt for generation
            aspect_ratio: Video aspect ratio (e.g., "16:9")
            duration: Video duration in seconds
            **kwargs: Additional parameters
            
        Returns:
            Generation result with video
        """
        params = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "duration": duration,
            **kwargs,
        }
        return await self.generate(model_id, params)
    
    async def generate_video_from_image(
        self,
        model_id: str,
        image_url: str,
        prompt: str,
        duration: int = 4,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Convenience method for image-to-video generation.
        
        Args:
            model_id: The image-to-video model identifier
            image_url: URL of the source image
            prompt: Motion/animation prompt
            duration: Video duration in seconds
            **kwargs: Additional parameters
            
        Returns:
            Generation result with video
        """
        params = {
            "image_url": image_url,
            "prompt": prompt,
            "duration": duration,
            **kwargs,
        }
        return await self.generate(model_id, params)
    
    async def generate_speech(
        self,
        model_id: str,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Convenience method for text-to-speech generation.
        
        Args:
            model_id: The TTS model identifier
            text: Text to convert to speech
            voice: Voice identifier
            speed: Speech speed multiplier
            **kwargs: Additional parameters
            
        Returns:
            Generation result with audio
        """
        params = {
            "text": text,
            "speed": speed,
            **kwargs,
        }
        if voice:
            params["voice"] = voice
        
        return await self.generate(model_id, params)
    
    def get_supported_models(self, gen_type: Optional[GenerationType] = None) -> list[str]:
        """
        Get list of supported model IDs.
        
        Args:
            gen_type: Optional filter by generation type
            
        Returns:
            List of model IDs
        """
        from app.registry import get_enabled_models, get_models_by_type
        
        if gen_type:
            models = get_models_by_type(gen_type)
        else:
            models = get_enabled_models()
        
        # Filter to only models with implemented providers
        return [
            model_id
            for model_id, model in models.items()
            if model.get("provider") in PROVIDER_HANDLERS
        ]


# Singleton instance
generation_service = GenerationService()

