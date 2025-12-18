"""
FAL OpenAPI Schema Service

Fetches and caches OpenAPI schemas from FAL's API for dynamic parameter validation.
"""

import time
import asyncio
from typing import Any, Optional
import httpx


# =============================================================================
# Types
# =============================================================================

class ParsedParameter:
    """Parsed parameter from OpenAPI schema."""
    
    def __init__(
        self,
        key: str,
        param_type: str,
        required: bool = False,
        default: Any = None,
        description: Optional[str] = None,
        enum: Optional[list] = None,
        minimum: Optional[float] = None,
        maximum: Optional[float] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        format: Optional[str] = None,
    ):
        self.key = key
        self.type = param_type
        self.required = required
        self.default = default
        self.description = description
        self.enum = enum
        self.minimum = minimum
        self.maximum = maximum
        self.min_length = min_length
        self.max_length = max_length
        self.format = format
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        result: dict[str, Any] = {
            "key": self.key,
            "type": self.type,
            "required": self.required,
        }
        if self.default is not None:
            result["default"] = self.default
        if self.description:
            result["description"] = self.description
        if self.enum:
            result["accepted_values"] = self.enum
        if self.minimum is not None:
            result["minimum"] = self.minimum
        if self.maximum is not None:
            result["maximum"] = self.maximum
        if self.min_length is not None:
            result["min_length"] = self.min_length
        if self.max_length is not None:
            result["max_length"] = self.max_length
        if self.format:
            result["format"] = self.format
        return result


class ParsedSchema:
    """Parsed OpenAPI schema with parameters."""
    
    def __init__(
        self,
        endpoint: str,
        parameters: list[ParsedParameter],
        error: Optional[str] = None,
    ):
        self.endpoint = endpoint
        self.parameters = parameters
        self.error = error
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "endpoint": self.endpoint,
            "parameters": [p.to_dict() for p in self.parameters],
            "error": self.error,
        }


# =============================================================================
# Cache
# =============================================================================

class SchemaCache:
    """In-memory cache for OpenAPI schemas with TTL."""
    
    def __init__(self, ttl: int = 300):
        """
        Initialize cache.
        
        Args:
            ttl: Time-to-live in seconds (default: 5 minutes)
        """
        self._cache: dict[str, tuple[ParsedSchema, float]] = {}
        self._ttl = ttl
    
    def get(self, key: str) -> Optional[ParsedSchema]:
        """Get a cached schema if not expired."""
        if key not in self._cache:
            return None
        
        schema, timestamp = self._cache[key]
        if time.time() - timestamp > self._ttl:
            # Expired
            del self._cache[key]
            return None
        
        return schema
    
    def set(self, key: str, schema: ParsedSchema) -> None:
        """Cache a schema."""
        self._cache[key] = (schema, time.time())
    
    def clear(self) -> None:
        """Clear all cached schemas."""
        self._cache.clear()


# =============================================================================
# Schema Parser
# =============================================================================

def _resolve_ref(ref: str, root_schema: dict) -> Optional[dict]:
    """Resolve a $ref path to the actual schema object."""
    if not ref.startswith("#/"):
        return None
    
    parts = ref[2:].split("/")
    current: Any = root_schema
    
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    
    return current if isinstance(current, dict) else None


def _resolve_schema(schema: dict, root_schema: dict) -> dict:
    """Recursively resolve a schema that may contain $ref, allOf, anyOf, or oneOf."""
    if not isinstance(schema, dict):
        return schema
    
    # Handle $ref
    if "$ref" in schema and isinstance(schema["$ref"], str):
        resolved = _resolve_ref(schema["$ref"], root_schema)
        if resolved:
            return _resolve_schema(resolved, root_schema)
        return schema
    
    # Handle allOf - merge all schemas
    if "allOf" in schema and isinstance(schema["allOf"], list):
        merged: dict[str, Any] = {}
        merged_properties: dict[str, Any] = {}
        merged_required: list[str] = []
        
        for sub_schema in schema["allOf"]:
            resolved = _resolve_schema(sub_schema, root_schema)
            merged.update(resolved)
            
            if "properties" in resolved and isinstance(resolved["properties"], dict):
                merged_properties.update(resolved["properties"])
            
            if "required" in resolved and isinstance(resolved["required"], list):
                merged_required.extend(resolved["required"])
        
        merged["properties"] = merged_properties
        merged["required"] = list(set(merged_required))
        return merged
    
    # Handle anyOf - merge all options' properties
    if "anyOf" in schema and isinstance(schema["anyOf"], list) and len(schema["anyOf"]) > 0:
        merged: dict[str, Any] = {}
        merged_properties: dict[str, Any] = {}
        
        for sub_schema in schema["anyOf"]:
            resolved = _resolve_schema(sub_schema, root_schema)
            if "properties" in resolved and isinstance(resolved["properties"], dict):
                merged_properties.update(resolved["properties"])
        
        if merged_properties:
            merged["properties"] = merged_properties
        return merged
    
    # Handle oneOf - take first option
    if "oneOf" in schema and isinstance(schema["oneOf"], list) and len(schema["oneOf"]) > 0:
        return _resolve_schema(schema["oneOf"][0], root_schema)
    
    # Resolve nested properties
    if "properties" in schema and isinstance(schema["properties"], dict):
        resolved_props = {}
        for key, prop in schema["properties"].items():
            if isinstance(prop, dict):
                resolved_props[key] = _resolve_schema(prop, root_schema)
            else:
                resolved_props[key] = prop
        return {**schema, "properties": resolved_props}
    
    return schema


def _extract_enum_from_any_of(prop: dict) -> Optional[list]:
    """Extract enum values from anyOf/oneOf const patterns."""
    any_of = prop.get("anyOf") or prop.get("oneOf")
    if not isinstance(any_of, list):
        return None
    
    enum_values = []
    for option in any_of:
        if isinstance(option, dict):
            if "const" in option and isinstance(option["const"], (str, int, float)):
                enum_values.append(option["const"])
            elif "enum" in option and isinstance(option["enum"], list):
                enum_values.extend(option["enum"])
            elif option.get("type") == "null":
                continue
    
    return enum_values if enum_values else None


def _parse_property(key: str, prop: dict, required: bool) -> ParsedParameter:
    """Parse an OpenAPI property to ParsedParameter."""
    param_type = prop.get("type", "string")
    
    # Extract enum from anyOf
    any_of_enum = _extract_enum_from_any_of(prop)
    enum_values = prop.get("enum") or any_of_enum
    
    # Infer type from anyOf enum if needed
    if any_of_enum and not param_type:
        param_type = "number" if isinstance(any_of_enum[0], (int, float)) else "string"
    
    # Get constraints
    minimum = prop.get("minimum") or prop.get("ge")
    maximum = prop.get("maximum") or prop.get("le")
    
    if prop.get("exclusiveMinimum") is not None:
        minimum = prop["exclusiveMinimum"] + 1
    if prop.get("exclusiveMaximum") is not None:
        maximum = prop["exclusiveMaximum"] - 1
    
    return ParsedParameter(
        key=key,
        param_type=param_type,
        required=required,
        default=prop.get("default"),
        description=prop.get("description"),
        enum=enum_values,
        minimum=minimum,
        maximum=maximum,
        min_length=prop.get("minLength"),
        max_length=prop.get("maxLength"),
        format=prop.get("format"),
    )


def _find_post_method(paths: dict) -> Optional[dict]:
    """Find POST method in OpenAPI paths."""
    # Try common path patterns
    for pattern in ["/", "/submit", "/queue"]:
        path_obj = paths.get(pattern)
        if isinstance(path_obj, dict) and "post" in path_obj:
            return path_obj["post"]
    
    # Try any path with POST
    for path_obj in paths.values():
        if isinstance(path_obj, dict) and "post" in path_obj:
            return path_obj["post"]
    
    return None


def parse_openapi_schema(schema: dict, endpoint_id: str) -> ParsedSchema:
    """Parse OpenAPI schema to extract input parameters."""
    parameters: list[ParsedParameter] = []
    
    try:
        paths = schema.get("paths")
        if not isinstance(paths, dict):
            return ParsedSchema(endpoint_id, [], "No paths found in schema")
        
        post_method = _find_post_method(paths)
        if not post_method:
            return ParsedSchema(endpoint_id, [], "No POST method found")
        
        request_body = post_method.get("requestBody", {})
        content = request_body.get("content", {})
        json_content = content.get("application/json", {})
        input_schema = json_content.get("schema")
        
        if not isinstance(input_schema, dict):
            return ParsedSchema(endpoint_id, [], "No input schema found")
        
        # Resolve refs
        input_schema = _resolve_schema(input_schema, schema)
        
        properties = input_schema.get("properties", {})
        required_fields = input_schema.get("required", [])
        
        if not isinstance(properties, dict) or not properties:
            return ParsedSchema(endpoint_id, [], "No properties found in schema")
        
        # Parse each property
        for key, prop in properties.items():
            # Skip internal/system fields
            if key.startswith("_") or key in ("webhookUrl", "sync_mode"):
                continue
            
            if isinstance(prop, dict):
                resolved_prop = _resolve_schema(prop, schema)
                is_required = key in required_fields
                parsed = _parse_property(key, resolved_prop, is_required)
                parameters.append(parsed)
        
        # Sort: required first, then alphabetically
        parameters.sort(key=lambda p: (not p.required, p.key))
        
        return ParsedSchema(endpoint_id, parameters)
        
    except Exception as e:
        return ParsedSchema(endpoint_id, [], f"Parse error: {str(e)}")


# =============================================================================
# Service
# =============================================================================

class FalSchemaService:
    """
    Service for fetching and caching FAL OpenAPI schemas.
    
    Used for dynamic parameter validation in the generation pipeline.
    """
    
    def __init__(self, cache_ttl: int = 300):
        """
        Initialize the schema service.
        
        Args:
            cache_ttl: Cache TTL in seconds (default: 5 minutes)
        """
        self._cache = SchemaCache(ttl=cache_ttl)
        self._http_client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client
    
    async def get_schema(self, endpoint_id: str) -> ParsedSchema:
        """
        Get the parsed schema for an endpoint.
        
        Checks cache first, then fetches from FAL's API if not cached.
        
        Args:
            endpoint_id: FAL endpoint ID (e.g., "fal-ai/veo3.1")
            
        Returns:
            ParsedSchema with parameters
        """
        # Check cache
        cached = self._cache.get(endpoint_id)
        if cached:
            return cached
        
        # Fetch from FAL
        try:
            client = await self._get_client()
            
            # Try Platform API first
            platform_url = f"https://api.fal.ai/v1/models?endpoint_id={endpoint_id}&expand=openapi-3.0"
            response = await client.get(platform_url)
            
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                if models and "openapi" in models[0]:
                    schema = parse_openapi_schema(models[0]["openapi"], endpoint_id)
                    self._cache.set(endpoint_id, schema)
                    return schema
            
            # Fallback to queue endpoint
            queue_url = f"https://fal.ai/api/openapi/queue/openapi.json?endpoint_id={endpoint_id}"
            response = await client.get(queue_url)
            
            if response.status_code != 200:
                error_schema = ParsedSchema(endpoint_id, [], f"FAL API error: {response.status_code}")
                return error_schema
            
            raw_schema = response.json()
            schema = parse_openapi_schema(raw_schema, endpoint_id)
            self._cache.set(endpoint_id, schema)
            return schema
            
        except Exception as e:
            return ParsedSchema(endpoint_id, [], f"Fetch error: {str(e)}")
    
    def get_schema_sync(self, endpoint_id: str) -> ParsedSchema:
        """
        Synchronous version of get_schema.
        
        Creates an event loop if needed.
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.get_schema(endpoint_id))
    
    def get_param_definitions(self, endpoint_id: str) -> dict[str, dict]:
        """
        Get parameter definitions as a dictionary keyed by parameter name.
        
        Compatible with the existing validate_params function format.
        
        Args:
            endpoint_id: FAL endpoint ID
            
        Returns:
            Dictionary of parameter definitions
        """
        schema = self.get_schema_sync(endpoint_id)
        return {p.key: p.to_dict() for p in schema.parameters}
    
    def clear_cache(self) -> None:
        """Clear the schema cache."""
        self._cache.clear()
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None


# Create singleton instance
fal_schema_service = FalSchemaService()






