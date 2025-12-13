"""Example: Complete Prompt → Overlay Flow.

This file demonstrates how agents use the prompt system to create video content.

Flow:
    1. User: "Create a video about remote work benefits"
    2. Writer Agent: Creates script with scenes
    3. System: Creates prompts from script (create_prompts_from_script)
    4. Producer Agent: Resolves video prompts with stock footage
    5. Editor Agent: Resolves text prompts, adds music
    6. Result: Complete timeline with all overlays linked to prompts
"""

# Example state after each step:

# =============================================================================
# STEP 1: User Request
# =============================================================================
# User says: "Create a 30-second video about remote work benefits"

initial_state = {
    "project": {
        "brief": "Create a 30-second video about remote work benefits",
        "aspect_ratio": "9:16",
        "target_duration": 30,
    },
    "script": None,
    "prompts": [],
    "timeline": {
        "overlays": [],
        "durationInFrames": 0,
        "width": 1080,
        "height": 1920,
        "fps": 30,
    }
}


# =============================================================================
# STEP 2: Writer Agent Creates Script
# =============================================================================
# Writer researches and creates script with scenes

after_writer = {
    "script": {
        "title": "Remote Work Benefits",
        "hook": "Discover why millions are embracing remote work",
        "scenes": [
            {
                "scene_number": 1,
                "duration": 5,
                "visual_description": "Person working happily from home on laptop",
                "search_keywords": ["remote work", "home office", "work from home"],
                "voice_over": "The future of work is here"
            },
            {
                "scene_number": 2,
                "duration": 5,
                "visual_description": "Video call with diverse remote team",
                "search_keywords": ["video call", "remote meeting", "zoom call"],
                "voice_over": "Connect with teams anywhere"
            },
            {
                "scene_number": 3,
                "duration": 5,
                "visual_description": "Person enjoying coffee in comfortable home setting",
                "search_keywords": ["coffee home", "relax home", "comfortable work"],
                "voice_over": "Work in your comfort zone"
            },
            {
                "scene_number": 4,
                "duration": 5,
                "visual_description": "Happy family spending time together",
                "search_keywords": ["family time", "work life balance", "happy family"],
                "voice_over": "More time for what matters"
            },
            {
                "scene_number": 5,
                "duration": 5,
                "visual_description": "Digital nomad working from beach or travel location",
                "search_keywords": ["digital nomad", "work travel", "laptop beach"],
                "voice_over": "Work from anywhere"
            },
            {
                "scene_number": 6,
                "duration": 5,
                "visual_description": "Productivity apps and tools on screen",
                "search_keywords": ["productivity", "work apps", "computer screen"],
                "voice_over": "Stay productive with the right tools"
            },
        ],
        "total_duration": 30
    },
    "prompts": [],  # Still empty - prompts created next
}


# =============================================================================
# STEP 3: Create Prompts from Script
# =============================================================================
# System calls create_prompts_from_script() to generate all prompts

after_prompts_created = {
    "prompts": [
        # Scene 1
        {
            "id": "prompt_001",
            "sceneIndex": 0,
            "type": "video",
            "instruction": "Person working happily from home on laptop",
            "params": {
                "keywords": ["remote work", "home office", "work from home"],
                "duration": 5,
                "provider": "pexels"
            },
            "status": "pending",
            "resolvedOverlayId": None
        },
        {
            "id": "prompt_002",
            "sceneIndex": 0,
            "type": "text",
            "instruction": "The future of work is here",
            "params": {"position": "bottom", "duration": 5},
            "status": "pending",
            "resolvedOverlayId": None
        },
        # Scene 2
        {
            "id": "prompt_003",
            "sceneIndex": 1,
            "type": "video",
            "instruction": "Video call with diverse remote team",
            "params": {
                "keywords": ["video call", "remote meeting", "zoom call"],
                "duration": 5,
                "provider": "pexels"
            },
            "status": "pending",
            "resolvedOverlayId": None
        },
        {
            "id": "prompt_004",
            "sceneIndex": 1,
            "type": "text",
            "instruction": "Connect with teams anywhere",
            "params": {"position": "bottom", "duration": 5},
            "status": "pending",
            "resolvedOverlayId": None
        },
        # ... more prompts for scenes 3-6
        
        # Global prompts (music)
        {
            "id": "prompt_013",
            "sceneIndex": None,  # Global - not tied to a scene
            "type": "music",
            "instruction": "Upbeat corporate background music",
            "params": {
                "mood": "upbeat",
                "duration": 30,
                "provider": "pixabay"
            },
            "status": "pending",
            "resolvedOverlayId": None
        },
    ],
}


# =============================================================================
# STEP 4: Producer Agent Resolves Video Prompts
# =============================================================================
# Producer searches stock footage and resolves each video prompt

after_producer = {
    "prompts": [
        {
            "id": "prompt_001",
            "sceneIndex": 0,
            "type": "video",
            "instruction": "Person working happily from home on laptop",
            "status": "resolved",  # Now resolved!
            "resolvedOverlayId": 1,  # Links to overlay
        },
        # ... other prompts
    ],
    
    "timeline": {
        "overlays": [
            {
                "id": 1,
                "type": "video",
                "promptId": "prompt_001",  # Links back to prompt!
                "status": "stock",
                "prompt": "Person working happily from home on laptop",
                "src": "https://videos.pexels.com/video-files/4145365/4145365-hd_1080_1920_25fps.mp4",
                "from": 0,
                "durationInFrames": 150,  # 5 seconds at 30fps
                "row": 0,
                "left": 0,
                "top": 0,
                "width": 1080,
                "height": 1920,
            },
            {
                "id": 2,
                "type": "video",
                "promptId": "prompt_003",
                "status": "stock",
                "prompt": "Video call with diverse remote team",
                "src": "https://videos.pexels.com/video-files/8865678/8865678-hd_1080_1920_30fps.mp4",
                "from": 150,  # Starts after scene 1
                "durationInFrames": 150,
                "row": 0,
            },
            # ... more video overlays
        ],
        "durationInFrames": 900,  # 30 seconds
    }
}


# =============================================================================
# STEP 5: Editor Agent Resolves Text & Audio Prompts
# =============================================================================
# Editor adds text overlays and background music

after_editor = {
    "timeline": {
        "overlays": [
            # Video overlays (from Producer)
            {"id": 1, "type": "video", "promptId": "prompt_001", "from": 0, "src": "https://..."},
            {"id": 2, "type": "video", "promptId": "prompt_003", "from": 150, "src": "https://..."},
            # ... more videos
            
            # Text overlays (from Editor)
            {
                "id": 7,
                "type": "text",
                "promptId": "prompt_002",  # Links to text prompt
                "status": "generated",
                "content": "The future of work is here",
                "from": 0,
                "durationInFrames": 150,
                "row": 1,
                "left": 50,
                "top": 1620,
                "width": 980,
                "height": 200,
                "styles": {
                    "fontSize": "3rem",
                    "fontWeight": "700",
                    "color": "#FFFFFF",
                    "backgroundColor": "rgba(0,0,0,0.5)",
                    "textAlign": "center"
                }
            },
            {
                "id": 8,
                "type": "text",
                "promptId": "prompt_004",
                "status": "generated",
                "content": "Connect with teams anywhere",
                "from": 150,
                "durationInFrames": 150,
                "row": 1,
            },
            # ... more text overlays
            
            # Background music (from Editor)
            {
                "id": 13,
                "type": "sound",
                "promptId": "prompt_013",  # Links to music prompt
                "status": "stock",
                "src": "https://pixabay.com/music/upbeat-corporate.mp3",
                "content": "Upbeat corporate background music",
                "from": 0,
                "durationInFrames": 900,  # Full video length
                "row": 2,
                "styles": {
                    "volume": 0.3,  # Lower volume for background
                    "fadeIn": 2,
                    "fadeOut": 2
                }
            }
        ],
        "durationInFrames": 900,
        "width": 1080,
        "height": 1920,
        "fps": 30
    }
}


# =============================================================================
# STEP 6: User Requests Change
# =============================================================================
# User: "Change scene 1 to show someone in a coffee shop instead"

# Agent finds the prompt for scene 1 video
# prompt_001.sceneIndex == 0 && prompt_001.type == "video"

# Agent updates the prompt:
after_user_change = {
    "prompts": [
        {
            "id": "prompt_001",
            "sceneIndex": 0,
            "type": "video",
            "instruction": "Person working on laptop in cozy coffee shop",  # Updated!
            "params": {
                "keywords": ["coffee shop laptop", "cafe work", "cozy coffee"],  # Updated!
                "duration": 5,
                "provider": "pexels"
            },
            "status": "pending",  # Reset to pending for re-resolution
            "resolvedOverlayId": 1,  # Still linked to same overlay
        },
    ],
    "timeline": {
        "overlays": [
            {
                "id": 1,
                "type": "video",
                "promptId": "prompt_001",
                "status": "prompt",  # Marked for regeneration!
                "prompt": "Person working on laptop in cozy coffee shop",  # Updated!
                "src": None,  # Cleared for new search
                "from": 0,
                "durationInFrames": 150,
            },
            # ... rest unchanged
        ]
    }
}

# Producer agent will then re-search and update overlay 1 with new stock footage


# =============================================================================
# KEY RELATIONSHIPS
# =============================================================================
"""
The bidirectional linking makes operations easy:

PROMPT → OVERLAY (via resolvedOverlayId):
    "Which overlay did this prompt create?"
    prompt = find_prompt(id="prompt_001")
    overlay = find_overlay(id=prompt.resolvedOverlayId)

OVERLAY → PROMPT (via promptId):
    "What prompt created this overlay?"
    overlay = find_overlay(id=1)
    prompt = find_prompt(id=overlay.promptId)

SCENE → PROMPTS → OVERLAYS:
    "What content is in scene 2?"
    scene_prompts = [p for p in prompts if p.sceneIndex == 1]
    scene_overlays = [find_overlay(p.resolvedOverlayId) for p in scene_prompts]

REGENERATION:
    "Regenerate all videos in scene 3"
    for prompt in prompts:
        if prompt.sceneIndex == 2 and prompt.type == "video":
            prompt.status = "pending"
            overlay = find_overlay(prompt.resolvedOverlayId)
            overlay.status = "prompt"
            overlay.src = None

STATUS TRACKING:
    "What still needs to be generated?"
    pending = [p for p in prompts if p.status == "pending"]
    unresolved_overlays = [o for o in overlays if o.status == "prompt"]
"""
