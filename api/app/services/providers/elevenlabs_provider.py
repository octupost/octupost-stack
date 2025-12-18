"""
ElevenLabs Provider Implementation

This provider handles ElevenLabs text-to-speech generation.
"""

import os
import uuid
from typing import Any

import httpx
import sentry_sdk

from app.config import get_settings
from .base import BaseProvider, Model


# ElevenLabs model definitions (multilingual models only)
ELEVENLABS_MODELS = {
    "eleven_v3": {
        "name": "Eleven v3 (alpha)",
        "description": "Best quality, newest model with 72 languages",
        "languages": 72,
    },
    "eleven_multilingual_v2": {
        "name": "Eleven Multilingual v2",
        "description": "High quality multilingual model with 29 languages",
        "languages": 29,
    },
    "eleven_flash_v2_5": {
        "name": "Eleven Flash v2.5",
        "description": "Fast model with good quality, 32 languages",
        "languages": 32,
    },
    "eleven_turbo_v2_5": {
        "name": "Eleven Turbo v2.5",
        "description": "Fastest multilingual model, 32 languages",
        "languages": 32,
    },
}

# Default voice settings
DEFAULT_VOICE_SETTINGS = {
    "stability": 0.5,
    "similarity_boost": 0.75,
    "style": 0.0,
    "use_speaker_boost": True,
}


class ElevenLabsProvider(BaseProvider):
    """
    Provider implementation for ElevenLabs text-to-speech.
    
    Supports:
    - Text-to-speech generation with multiple models
    - Voice selection and customization
    - Voice settings (stability, similarity, style, speed)
    """
    
    BASE_URL = "https://api.elevenlabs.io/v1"
    
    def __init__(self, provider_config: dict[str, Any] = None):
        """Initialize the ElevenLabs provider."""
        if provider_config is None:
            provider_config = {
                "name": "ElevenLabs",
                "type": "api",
                "authMethod": "api-key",
                "authEnvVar": "ELEVENLABS_API_KEY",
                "baseUrl": self.BASE_URL,
                "capabilities": ["text-to-speech"],
                "responseMapping": {},
            }
        super().__init__(provider_config)
        self._api_key = os.environ.get("ELEVENLABS_API_KEY", "")
    
    @property
    def api_key(self) -> str:
        """Get the ElevenLabs API key."""
        if not self._api_key:
            self._api_key = os.environ.get("ELEVENLABS_API_KEY", "")
        return self._api_key
    
    def _get_headers(self) -> dict[str, str]:
        """Get headers for ElevenLabs API requests."""
        return {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
        }
    
    async def generate(
        self,
        model_id: str,
        model_config: Model,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute text-to-speech generation using ElevenLabs.
        
        Args:
            model_id: The model identifier (e.g., "elevenlabs/eleven_multilingual_v2")
            model_config: Model configuration (may be empty for ElevenLabs)
            params: Generation parameters:
                - text: Text to convert to speech (required)
                - voice_id: Voice ID to use (required)
                - model_id: ElevenLabs model ID (optional, defaults from model_id)
                - stability: Voice stability 0-1 (optional)
                - similarity_boost: Voice similarity 0-1 (optional)
                - style: Style exaggeration 0-1 (optional)
                - speed: Speech speed 0.5-2 (optional)
            
        Returns:
            Normalized result dictionary with audio URL and duration
        """
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable is not set")
        
        text = params.get("text", "")
        if not text:
            raise ValueError("Text is required for text-to-speech generation")
        
        voice_id = params.get("voice_id", params.get("voice", ""))
        if not voice_id:
            # Default to a common voice if not specified
            voice_id = "EXAVITQu4vr4xnSDxMaL"  # Sarah
        
        # Extract ElevenLabs model from model_id
        el_model_id = self._extract_elevenlabs_model(model_id, params)
        
        # Build voice settings
        voice_settings = {
            "stability": params.get("stability", DEFAULT_VOICE_SETTINGS["stability"]),
            "similarity_boost": params.get("similarity_boost", DEFAULT_VOICE_SETTINGS["similarity_boost"]),
            "style": params.get("style", DEFAULT_VOICE_SETTINGS["style"]),
            "use_speaker_boost": params.get("use_speaker_boost", DEFAULT_VOICE_SETTINGS["use_speaker_boost"]),
        }
        
        # Build request payload
        payload = {
            "text": text,
            "model_id": el_model_id,
            "voice_settings": voice_settings,
        }
        
        # Add speed if specified (only some models support it)
        if "speed" in params and params["speed"] != 1.0:
            payload["speed"] = params["speed"]
        
        sentry_sdk.set_context("elevenlabs", {
            "voice_id": voice_id,
            "model_id": el_model_id,
            "text_length": len(text),
        })
        
        # Make the TTS request
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.BASE_URL}/text-to-speech/{voice_id}",
                headers=self._get_headers(),
                json=payload,
            )
            
            if response.status_code != 200:
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = error_json.get("detail", {}).get("message", error_detail)
                except Exception:
                    pass
                raise ValueError(f"ElevenLabs API error ({response.status_code}): {error_detail}")
            
            audio_bytes = response.content
            content_type = response.headers.get("content-type", "audio/mpeg")
        
        # Upload to Supabase storage and get URL
        audio_url = await self._upload_audio_to_storage(audio_bytes, content_type)
        
        # Estimate duration based on character count (rough estimate: ~150 chars per minute)
        estimated_duration = len(text) / 150 * 60  # seconds
        
        return {
            "audio": {
                "url": audio_url,
                "duration": estimated_duration,
                "content_type": content_type,
            },
            "text": text,
            "voice": voice_id,
            "model": el_model_id,
        }
    
    def _extract_elevenlabs_model(self, model_id: str, params: dict[str, Any]) -> str:
        """
        Extract the ElevenLabs model ID from the model identifier.
        
        Args:
            model_id: Full model ID (e.g., "elevenlabs/eleven_multilingual_v2")
            params: Request params that may contain model_id override
            
        Returns:
            ElevenLabs model ID (e.g., "eleven_multilingual_v2")
        """
        # Check if model_id is overridden in params
        if "model_id" in params:
            return params["model_id"]
        
        # Extract from full model ID
        if "/" in model_id:
            parts = model_id.split("/")
            if len(parts) >= 2:
                return parts[1]
        
        # Check if it's already a valid ElevenLabs model ID
        if model_id in ELEVENLABS_MODELS:
            return model_id
        
        # Default to multilingual v2
        return "eleven_multilingual_v2"
    
    async def _upload_audio_to_storage(
        self,
        audio_bytes: bytes,
        content_type: str,
    ) -> str:
        """
        Upload audio bytes to Supabase storage and return the public URL.
        
        Args:
            audio_bytes: The audio file content
            content_type: MIME type of the audio
            
        Returns:
            Public URL of the uploaded audio
        """
        from app.services.supabase_client import supabase_service
        
        if not supabase_service.client:
            raise ValueError("Supabase is not configured - cannot upload audio")
        
        # Determine file extension from content type
        ext = "mp3"
        if "wav" in content_type:
            ext = "wav"
        elif "ogg" in content_type:
            ext = "ogg"
        elif "flac" in content_type:
            ext = "flac"
        
        # Generate unique file path
        file_name = f"{uuid.uuid4()}.{ext}"
        file_path = f"elevenlabs/{file_name}"
        
        # Upload to Supabase storage
        result = supabase_service.client.storage.from_("assets").upload(
            path=file_path,
            file=audio_bytes,
            file_options={"content-type": content_type},
        )
        
        if hasattr(result, "error") and result.error:
            raise ValueError(f"Failed to upload audio: {result.error}")
        
        # Get public URL
        url_result = supabase_service.client.storage.from_("assets").get_public_url(file_path)
        
        return url_result
    
    async def get_voices(self) -> list[dict[str, Any]]:
        """
        Get available voices from ElevenLabs.
        
        Returns:
            List of voice dictionaries with id, name, category, etc.
        """
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable is not set")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/voices",
                headers=self._get_headers(),
            )
            
            if response.status_code != 200:
                raise ValueError(f"Failed to fetch voices: {response.status_code}")
            
            data = response.json()
            voices = data.get("voices", [])
            
            # Normalize voice data
            return [
                {
                    "id": v.get("voice_id"),
                    "name": v.get("name"),
                    "category": v.get("category", "premade"),
                    "description": v.get("description", ""),
                    "preview_url": v.get("preview_url"),
                    "labels": v.get("labels", {}),
                }
                for v in voices
            ]
    
    async def get_voice(self, voice_id: str) -> dict[str, Any]:
        """
        Get details for a specific voice.
        
        Args:
            voice_id: The voice ID to look up
            
        Returns:
            Voice details dictionary
        """
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable is not set")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/voices/{voice_id}",
                headers=self._get_headers(),
            )
            
            if response.status_code != 200:
                raise ValueError(f"Failed to fetch voice: {response.status_code}")
            
            v = response.json()
            
            return {
                "id": v.get("voice_id"),
                "name": v.get("name"),
                "category": v.get("category", "premade"),
                "description": v.get("description", ""),
                "preview_url": v.get("preview_url"),
                "labels": v.get("labels", {}),
                "settings": v.get("settings", DEFAULT_VOICE_SETTINGS),
            }
    
    def get_models(self) -> list[dict[str, Any]]:
        """
        Get available ElevenLabs TTS models.
        
        Returns:
            List of model definitions
        """
        return [
            {
                "id": model_id,
                "name": info["name"],
                "description": info["description"],
                "languages": info["languages"],
            }
            for model_id, info in ELEVENLABS_MODELS.items()
        ]


# Singleton instance
elevenlabs_provider = ElevenLabsProvider()

