"""Pexels stock video search tool for the Content Team."""

from typing import Optional

import httpx
from agno.tools import Toolkit


class PexelsSearchTool(Toolkit):
    """Search Pexels for stock videos."""
    
    def __init__(self, api_key: str):
        super().__init__(name="pexels_search")
        self.api_key = api_key
        self.base_url = "https://api.pexels.com/videos"
        self.register(self.search_videos)
    
    def search_videos(
        self, 
        query: str, 
        orientation: str = "landscape",  # landscape, portrait, square
        per_page: int = 5,
        min_duration: Optional[int] = None,
        max_duration: Optional[int] = None,
    ) -> list:
        """
        Search Pexels for videos matching query.
        
        Args:
            query: Search keywords (e.g., "person working laptop", "city skyline sunset")
            orientation: Video orientation - "landscape" (16:9), "portrait" (9:16), or "square" (1:1)
            per_page: Number of results to return (max 80)
            min_duration: Minimum video duration in seconds
            max_duration: Maximum video duration in seconds
        
        Returns:
            List of video results with URLs and metadata
        """
        params = {
            "query": query,
            "orientation": orientation,
            "per_page": per_page,
        }
        
        if min_duration:
            params["min_duration"] = min_duration
        if max_duration:
            params["max_duration"] = max_duration
        
        try:
            response = httpx.get(
                f"{self.base_url}/search",
                params=params,
                headers={"Authorization": self.api_key},
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for video in data.get("videos", []):
                # Get the best quality video file (prefer HD)
                video_files = video.get("video_files", [])
                hd_file = next(
                    (f for f in video_files if f.get("quality") == "hd"),
                    video_files[0] if video_files else None
                )
                
                if hd_file:
                    results.append({
                        "id": video["id"],
                        "url": video["url"],
                        "video_url": hd_file["link"],
                        "duration": video["duration"],
                        "width": hd_file.get("width", video.get("width")),
                        "height": hd_file.get("height", video.get("height")),
                        "quality": hd_file.get("quality", "unknown"),
                        "source": "pexels",
                        "attribution": f"Video by {video['user']['name']} from Pexels",
                        "user": video["user"]["name"],
                    })
            
            return results
            
        except httpx.HTTPError as e:
            return [{"error": f"Pexels API error: {str(e)}"}]
        except Exception as e:
            return [{"error": f"Unexpected error: {str(e)}"}]

