"""
Base Provider Interface

Abstract base class for AI provider implementations. All providers
(Fal AI, Runway, ElevenLabs, etc.) must implement this interface.
"""

from abc import ABC, abstractmethod
from typing import Any, Literal, Optional, TypedDict


# Provider type definitions
ProviderType = Literal["sdk", "rest", "websocket"]
AuthMethod = Literal["api-key", "oauth", "bearer"]


class Provider(TypedDict, total=False):
    """Provider configuration."""
    name: str
    type: ProviderType
    sdkPackage: Optional[str]
    authMethod: AuthMethod
    authEnvVar: str
    baseUrl: Optional[str]
    capabilities: list[str]
    responseMapping: dict[str, str]


# Model configuration type (simplified)
Model = dict[str, Any]


class BaseProvider(ABC):
    """
    Abstract base class for AI provider implementations.
    
    Each provider must implement the generate() method which handles
    the actual API call to the provider's service.
    """
    
    def __init__(self, provider_config: Provider):
        """
        Initialize the provider with its configuration.
        
        Args:
            provider_config: Provider configuration
        """
        self.config = provider_config
    
    @abstractmethod
    async def generate(
        self,
        model_id: str,
        model_config: Model,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute generation and return normalized result.
        
        Args:
            model_id: The model identifier (e.g., "fal-ai/flux/schnell")
            model_config: Model configuration from the registry
            params: Generation parameters
            
        Returns:
            Normalized result dictionary with standard keys:
            - For images: {"images": [...], "seed": int}
            - For video: {"video": {...}, "seed": int}
            - For audio: {"audio": {...}}
        """
        pass
    
    def map_parameters(
        self,
        params: dict[str, Any],
        mapping: dict[str, str],
    ) -> dict[str, Any]:
        """
        Map standard parameter names to provider-specific names.
        
        Args:
            params: Input parameters with standard names
            mapping: Mapping of standard names to provider-specific names
            
        Returns:
            Parameters with provider-specific names
        """
        if not mapping:
            return params.copy()
        
        result: dict[str, Any] = {}
        
        for key, value in params.items():
            mapped_key = mapping.get(key, key)
            
            # Handle nested keys like "image_size.width"
            if "." in mapped_key:
                parts = mapped_key.split(".")
                if parts[0] not in result:
                    result[parts[0]] = {}
                result[parts[0]][parts[1]] = value
            else:
                result[mapped_key] = value
        
        return result
    
    def apply_transforms(
        self,
        params: dict[str, Any],
        transforms: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Apply parameter transformations.
        
        Args:
            params: Input parameters
            transforms: Transform definitions from model config
            
        Returns:
            Transformed parameters
        """
        if not transforms:
            return params.copy()
        
        result = params.copy()
        
        for key, transform in transforms.items():
            if key not in result:
                continue
            
            value = result[key]
            
            if not isinstance(value, (int, float)):
                continue
            
            # Apply transforms in order
            if "min" in transform:
                value = max(value, transform["min"])
            if "max" in transform:
                value = min(value, transform["max"])
            if "multiply" in transform:
                value = int(value * transform["multiply"])
            
            result[key] = value
        
        return result
    
    def merge_defaults(
        self,
        params: dict[str, Any],
        defaults: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Merge default parameters with provided parameters.
        
        Args:
            params: User-provided parameters
            defaults: Default parameters from model config
            
        Returns:
            Merged parameters (user params take precedence)
        """
        result = defaults.copy()
        result.update(params)
        return result
    
    def get_endpoint(self, model_config: Model) -> str:
        """
        Get the API endpoint for a model.
        
        Args:
            model_config: Model configuration
            
        Returns:
            API endpoint path or model identifier
        """
        provider_config = model_config.get("providerConfig", {})
        return provider_config.get("endpoint", "")

