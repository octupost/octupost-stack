"""Pixabay stock video search tool for the Content Team."""

from typing import Optional

import httpx
from agno.tools import Toolkit


class PixabaySearchTool(Toolkit):
    """Search Pixabay for stock videos."""
    
    def __init__(self, api_key: str):
        super().__init__(name="pixabay_search")
        self.api_key = api_key
        self.base_url = "https://pixabay.com/api/videos"
        self.register(self.search_videos)
    
    def search_videos(
        self, 
        query: str,
        video_type: str = "all",  # all, film, animation
        per_page: int = 5,
        min_width: Optional[int] = None,
        min_height: Optional[int] = None,
    ) -> list:
        """
        Search Pixabay for videos matching query.
        
        Args:
            query: Search keywords (e.g., "nature landscape", "business office")
            video_type: Type of video - "all", "film", or "animation"
            per_page: Number of results to return (max 200)
            min_width: Minimum video width in pixels
            min_height: Minimum video height in pixels
        
        Returns:
            List of video results with URLs and metadata
        """
        params = {
            "key": self.api_key,
            "q": query,
            "video_type": video_type,
            "per_page": per_page,
            "safesearch": "true",
        }
        
        if min_width:
            params["min_width"] = min_width
        if min_height:
            params["min_height"] = min_height
        
        try:
            response = httpx.get(
                self.base_url,
                params=params,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for video in data.get("hits", []):
                videos = video.get("videos", {})
                # Prefer large, fall back to medium
                video_file = videos.get("large", videos.get("medium", {}))
                
                if video_file:
                    results.append({
                        "id": video["id"],
                        "video_url": video_file.get("url", ""),
                        "duration": video.get("duration", 0),
                        "width": video_file.get("width", 0),
                        "height": video_file.get("height", 0),
                        "source": "pixabay",
                        "attribution": f"Video by {video.get('user', 'Unknown')} from Pixabay",
                        "user": video.get("user", "Unknown"),
                        "tags": video.get("tags", ""),
                        "video_files": {
                            "large": videos.get("large", {}).get("url", ""),
                            "medium": videos.get("medium", {}).get("url", ""),
                            "small": videos.get("small", {}).get("url", ""),
                        },
                    })
            
            return results
            
        except httpx.HTTPError as e:
            return [{"error": f"Pixabay API error: {str(e)}"}]
        except Exception as e:
            return [{"error": f"Unexpected error: {str(e)}"}]

