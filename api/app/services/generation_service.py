"""
Unified Generation Service

This service provides a single entry point for all AI generation requests,
routing to the appropriate provider based on the model's configuration.
"""

from typing import Any, Literal, Optional, Type

# Generation types supported by the system
GenerationType = Literal[
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
    "text-generation",
]

from .providers.base import BaseProvider
from .providers.fal_provider import FalProvider
from .providers.elevenlabs_provider import ElevenLabsProvider
from .supabase_client import supabase_service


# Provider registry mapping provider IDs to their implementations
PROVIDER_HANDLERS: dict[str, Type[BaseProvider]] = {
    "fal-ai": FalProvider,
    "elevenlabs": ElevenLabsProvider,
    # Future providers:
    # "runway": RunwayProvider,
    # "openai": OpenAIProvider,
}


def _get_provider_id_from_endpoint(endpoint: str) -> str:
    """
    Determine the provider ID from the model endpoint.
    
    NO FALLBACK - endpoint must match a known provider prefix.
    
    Args:
        endpoint: The model endpoint (e.g., "fal-ai/veo3.1", "elevenlabs/eleven_multilingual_v2")
        
    Returns:
        Provider ID (e.g., "fal-ai", "elevenlabs")
        
    Raises:
        ValueError: If endpoint doesn't match any known provider
    """
    if endpoint.startswith("fal-ai/"):
        return "fal-ai"
    if endpoint.startswith("elevenlabs/"):
        return "elevenlabs"
    # Add other provider detection here
    # if endpoint.startswith("runway/"):
    #     return "runway"
    
    # NO FALLBACK - raise error for unknown providers
    raise ValueError(
        f"Unknown provider for endpoint: {endpoint}. "
        "Endpoint must start with a known provider prefix (e.g., 'fal-ai/', 'elevenlabs/')."
    )


class GenerationService:
    """
    Unified service for AI generation requests.
    
    Routes requests to the appropriate provider based on the model's
    configuration in the registry (provider.json).
    
    Example:
        service = GenerationService()
        result = await service.generate(
            model_id="fal-ai/veo3.1",
            params={"prompt": "A beautiful sunset", "duration": 4}
        )
    """
    
    def __init__(self):
        """Initialize the generation service."""
        self._provider_instances: dict[str, BaseProvider] = {}
    
    def _get_provider_instance(self, provider_id: str) -> Optional[BaseProvider]:
        """
        Get or create a provider instance.
        
        Args:
            provider_id: The provider identifier (e.g., "fal-ai", "elevenlabs")
            
        Returns:
            Provider instance or None if not found
        """
        if provider_id in self._provider_instances:
            return self._provider_instances[provider_id]
        
        provider_class = PROVIDER_HANDLERS.get(provider_id)
        if not provider_class:
            return None
        
        # Provider-specific configurations
        provider_configs = {
            "fal-ai": {
                "name": "fal-ai",
                "type": "sdk",
                "sdkPackage": "fal-client",
                "authMethod": "api-key",
                "authEnvVar": "FAL_KEY",
                "baseUrl": None,
                "capabilities": [],
                "responseMapping": {},
            },
            "elevenlabs": {
                "name": "ElevenLabs",
                "type": "api",
                "authMethod": "api-key",
                "authEnvVar": "ELEVENLABS_API_KEY",
                "baseUrl": "https://api.elevenlabs.io/v1",
                "capabilities": ["text-to-speech"],
                "responseMapping": {},
            },
        }
        
        provider_config = provider_configs.get(provider_id, {
            "name": provider_id,
            "type": "api",
            "authMethod": "api-key",
            "baseUrl": None,
            "capabilities": [],
            "responseMapping": {},
        })
        
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
            model_id: The model identifier/endpoint (e.g., "fal-ai/veo3.1", "elevenlabs/eleven_multilingual_v2")
            params: Generation parameters
            validate: Whether to validate parameters before generation
            
        Returns:
            Normalized generation result
            
        Raises:
            ValueError: If model is invalid or provider not implemented
        """
        # Get model configuration from database - NO FALLBACK
        # All models (including ElevenLabs) must be configured in the database
        model_config = supabase_service.get_model_config(model_id)
        
        if not model_config:
            raise ValueError(
                f"Unknown model: {model_id}. "
                "All models must be configured in the database."
            )
        
        # Check if model is active
        if not model_config.get("is_active", False):
            raise ValueError(f"Model {model_id} is not active")
        
        # Determine provider from endpoint
        endpoint = model_config.get("endpoint", model_id)
        provider_id = _get_provider_id_from_endpoint(endpoint)
        
        # Get provider instance
        provider = self._get_provider_instance(provider_id)
        if not provider:
            raise ValueError(f"Provider not implemented: {provider_id}")
        
        # Execute generation - the provider will handle parameter transformation
        return await provider.generate(model_id, model_config, params)
    
    async def generate_image(
        self,
        model_id: str,
        prompt: str,
        aspect_ratio: str = "1:1",
        resolution: Optional[str] = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Convenience method for image generation.
        
        Args:
            model_id: The image model identifier
            prompt: Text prompt for generation
            aspect_ratio: Image aspect ratio
            resolution: Image resolution/quality
            **kwargs: Additional parameters
            
        Returns:
            Generation result with images
        """
        params = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            **kwargs,
        }
        if resolution:
            params["resolution"] = resolution
        return await self.generate(model_id, params)
    
    async def generate_video(
        self,
        model_id: str,
        prompt: str,
        aspect_ratio: str = "16:9",
        duration: int = 4,
        resolution: str = "1080p",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Convenience method for video generation.
        
        Args:
            model_id: The video model identifier
            prompt: Text prompt for generation
            aspect_ratio: Video aspect ratio (e.g., "16:9")
            duration: Video duration in seconds
            resolution: Video resolution
            **kwargs: Additional parameters
            
        Returns:
            Generation result with video
        """
        params = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "duration": duration,
            "resolution": resolution,
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
        speech_speed: float = 1.0,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Convenience method for text-to-speech generation.
        
        Args:
            model_id: The TTS model identifier
            text: Text to convert to speech
            voice: Voice identifier
            speech_speed: Speech speed multiplier
            **kwargs: Additional parameters
            
        Returns:
            Generation result with audio
        """
        params = {
            "text": text,
            "speech_speed": speech_speed,
            **kwargs,
        }
        if voice:
            params["voice"] = voice
        
        return await self.generate(model_id, params)
    
    async def generate_audio(
        self,
        model_id: str,
        prompt: str,
        duration: int = 10,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Convenience method for audio/music generation.
        
        Args:
            model_id: The audio model identifier
            prompt: Text prompt for generation
            duration: Audio duration in seconds
            **kwargs: Additional parameters
            
        Returns:
            Generation result with audio
        """
        params = {
            "prompt": prompt,
            "duration": duration,
            **kwargs,
        }
        return await self.generate(model_id, params)
    
    def get_supported_models(self, gen_type: Optional[GenerationType] = None) -> list[str]:
        """
        Get list of supported model IDs.
        
        Args:
            gen_type: Optional filter by generation type
            
        Returns:
            List of model IDs (endpoints)
        """
        client = supabase_service.client
        if not client:
            return []
        
        try:
            query = client.schema("octupost").table("model_configs").select("endpoint").eq("is_active", True)
            
            if gen_type:
                query = query.eq("type", gen_type)
            
            result = query.execute()
            return [row["endpoint"] for row in result.data] if result.data else []
        except Exception:
            return []


# Singleton instance
generation_service = GenerationService()
