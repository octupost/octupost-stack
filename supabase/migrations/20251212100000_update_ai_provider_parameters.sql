-- =============================================================================
-- UPDATE AI PROVIDER PARAMETERS
-- =============================================================================
-- Created: 2024-12-12
-- Purpose: Update the parameters column in octupost.ai_providers table
--          with new parameter definitions from providerV1.json
-- 
-- This migration matches on the endpoint column and replaces the parameters
-- column with the corresponding parameter definitions.
-- =============================================================================

BEGIN;

-- fal-ai/longcat-video/image-to-video/720p
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 1,
      "max_duration": 30,
      "min_duration": 2
    },
    "default": 4,
    "required": true,
    "mapping": "num_frames",
    "mapping_type": "integer",
    "notes": "Multiply second by 30 to get the number of frames"
  },
  {
    "key": "resolution",
    "type": "string",
    "accepted_values": ["720p"],
    "default": "720p",
    "required": true,
    "mapping": "resolution",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["16:9", "9:16", "1:1"],
    "default": "9:16",
    "required": true,
    "mapping": "aspect_ratio",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "negative_prompt",
    "type": "string",
    "default": "",
    "required": false,
    "mapping": "negative_prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "image_url",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "image_url",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "enhance_prompt",
    "type": "boolean",
    "required": false,
    "mapping": "enable_prompt_expansion",
    "mapping_type": "boolean",
    "notes": ""
  },
  {
    "default_values": {
      "fps": 30,
      "num_inference_steps": 12,
      "num_refine_inference_steps": 12,
      "seed": 42,
      "enable_safety_checker": true,
      "video_output_type": "X264 (.mp4)",
      "video_quality": "high",
      "video_write_mode": "balanced",
      "sync_mode": false
    }
  }
]'::jsonb
WHERE endpoint = 'fal-ai/longcat-video/image-to-video/720p';

-- fal-ai/longcat-video/text-to-video/720p
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 1,
      "max_duration": 30,
      "min_duration": 2
    },
    "default": 4,
    "required": true,
    "mapping": "duration",
    "mapping_type": "integer",
    "notes": "Multiply second by 30 to get the number of frames"
  },
  {
    "key": "resolution",
    "type": "string",
    "accepted_values": ["720p"],
    "default": "720p",
    "required": true,
    "mapping": "resolution",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["16:9", "9:16", "1:1"],
    "default": "9:16",
    "required": true,
    "mapping": "aspect_ratio",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "negative_prompt",
    "type": "string",
    "default": "",
    "required": false,
    "mapping": "negative_prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "enhance_prompt",
    "type": "boolean",
    "required": false,
    "mapping": "enhance_prompt",
    "mapping_type": "boolean",
    "notes": ""
  },
  {
    "default_values": {
      "fps": 30,
      "num_inference_steps": 12,
      "num_refine_inference_steps": 12,
      "seed": 42,
      "enable_safety_checker": true,
      "video_output_type": "X264 (.mp4)",
      "video_quality": "high",
      "video_write_mode": "balanced",
      "sync_mode": false
    }
  }
]'::jsonb
WHERE endpoint = 'fal-ai/longcat-video/text-to-video/720p';

-- fal-ai/longcat-video/distilled/image-to-video/720p
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 1,
      "max_duration": 30,
      "min_duration": 2
    },
    "default": 4,
    "required": true,
    "mapping": "num_frames",
    "mapping_type": "integer",
    "notes": "Multiply second by 30 to get the number of frames"
  },
  {
    "key": "resolution",
    "type": "string",
    "accepted_values": ["720p"],
    "default": "720p",
    "required": true,
    "mapping": "resolution",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["16:9", "9:16", "1:1"],
    "default": "9:16",
    "required": true,
    "mapping": "aspect_ratio",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "negative_prompt",
    "type": "string",
    "default": "",
    "required": false,
    "mapping": "negative_prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "image_url",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "image_url",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "enhance_prompt",
    "type": "boolean",
    "required": false,
    "mapping": "enable_prompt_expansion",
    "mapping_type": "boolean",
    "notes": ""
  },
  {
    "default_values": {
      "fps": 30,
      "num_inference_steps": 12,
      "num_refine_inference_steps": 12,
      "seed": 42,
      "enable_safety_checker": true,
      "video_output_type": "X264 (.mp4)",
      "video_quality": "high",
      "video_write_mode": "balanced",
      "sync_mode": false
    }
  }
]'::jsonb
WHERE endpoint = 'fal-ai/longcat-video/distilled/image-to-video/720p';

-- fal-ai/longcat-video/distilled/text-to-video/720p
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 1,
      "max_duration": 30,
      "min_duration": 2
    },
    "default": 4,
    "required": true,
    "mapping": "duration",
    "mapping_type": "integer",
    "notes": "Multiply second by 30 to get the number of frames"
  },
  {
    "key": "resolution",
    "type": "string",
    "accepted_values": ["720p"],
    "default": "720p",
    "required": true,
    "mapping": "resolution",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["16:9", "9:16", "1:1"],
    "default": "9:16",
    "required": true,
    "mapping": "aspect_ratio",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "negative_prompt",
    "type": "string",
    "default": "",
    "required": false,
    "mapping": "negative_prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "enhance_prompt",
    "type": "boolean",
    "required": false,
    "mapping": "enhance_prompt",
    "mapping_type": "boolean",
    "notes": ""
  },
  {
    "default_values": {
      "fps": 30,
      "num_inference_steps": 12,
      "num_refine_inference_steps": 12,
      "seed": 42,
      "enable_safety_checker": true,
      "video_output_type": "X264 (.mp4)",
      "video_quality": "high",
      "video_write_mode": "balanced",
      "sync_mode": false
    }
  }
]'::jsonb
WHERE endpoint = 'fal-ai/longcat-video/distilled/text-to-video/720p';

-- fal-ai/veo3.1/fast
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 2,
      "max_duration": 8,
      "min_duration": 4
    },
    "default": 4,
    "required": true,
    "mapping": "duration",
    "mapping_type": "string",
    "notes": "Add s at the end of the duration"
  },
  {
    "key": "resolution",
    "type": "string",
    "accepted_values": ["720p", "1080p"],
    "default": "720p",
    "required": true,
    "mapping": "resolution",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "negative_prompt",
    "type": "string",
    "default": "",
    "required": false,
    "mapping": "negative_prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["16:9", "9:16"],
    "default": "16:9",
    "required": true,
    "mapping": "aspect_ratio",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "enable_audio",
    "type": "boolean",
    "required": true,
    "mapping": "generate_audio",
    "mapping_type": "boolean",
    "notes": ""
  },
  {
    "default_values": {
      "auto_fix": true
    }
  }
]'::jsonb
WHERE endpoint = 'fal-ai/veo3.1/fast';

-- fal-ai/veo3.1
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 2,
      "max_duration": 8,
      "min_duration": 4
    },
    "default": 4,
    "required": true,
    "mapping": "duration",
    "mapping_type": "string",
    "notes": "Add s at the end of the duration"
  },
  {
    "key": "resolution",
    "type": "string",
    "accepted_values": ["720p", "1080p"],
    "default": "720p",
    "required": true,
    "mapping": "resolution",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "negative_prompt",
    "type": "string",
    "default": "",
    "required": false,
    "mapping": "negative_prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["16:9", "9:16"],
    "default": "16:9",
    "required": true,
    "mapping": "aspect_ratio",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "enable_audio",
    "type": "boolean",
    "required": true,
    "mapping": "generate_audio",
    "mapping_type": "boolean",
    "notes": ""
  },
  {
    "default_values": {
      "auto_fix": true
    }
  }
]'::jsonb
WHERE endpoint = 'fal-ai/veo3.1';

-- fal-ai/veo3.1/fast/image-to-video
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "image_url",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "image_url",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 2,
      "max_duration": 8,
      "min_duration": 4
    },
    "default": 4,
    "required": true,
    "mapping": "duration",
    "mapping_type": "string",
    "notes": "Add s at the end of the duration"
  },
  {
    "key": "resolution",
    "type": "string",
    "accepted_values": ["720p", "1080p"],
    "default": "1080p",
    "required": true,
    "mapping": "resolution",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["auto", "16:9", "9:16"],
    "default": "auto",
    "required": true,
    "mapping": "aspect_ratio",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "enable_audio",
    "type": "boolean",
    "required": true,
    "mapping": "generate_audio",
    "mapping_type": "boolean",
    "notes": ""
  },
  {
    "default_values": {
      "auto_fix": true
    }
  }
]'::jsonb
WHERE endpoint = 'fal-ai/veo3.1/fast/image-to-video';

-- fal-ai/veo3.1/reference-to-video
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "image_urls[0]",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "image_urls[0]",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "image_urls[1]",
    "type": "string",
    "default": "",
    "required": false,
    "mapping": "image_urls[1]",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "image_urls[2]",
    "type": "string",
    "default": "",
    "required": false,
    "mapping": "image_urls[2]",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 0,
      "max_duration": 8,
      "min_duration": 8
    },
    "default": 8,
    "required": true,
    "mapping": "duration",
    "mapping_type": "string",
    "notes": "Add s at the end of the duration"
  },
  {
    "key": "resolution",
    "type": "string",
    "accepted_values": ["720p", "1080p"],
    "default": "720p",
    "required": true,
    "mapping": "resolution",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["16:9"],
    "default": "16:9",
    "required": true,
    "mapping": "aspect_ratio",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "enable_audio",
    "type": "boolean",
    "default": false,
    "required": true,
    "mapping": "generate_audio",
    "mapping_type": "boolean",
    "notes": ""
  },
  {
    "key": "negative_prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "negative_prompt",
    "mapping_type": "string",
    "notes": "This is the negative prompt for the video"
  },
  {
    "default_values": {
      "auto_fix": true
    }
  }
]'::jsonb
WHERE endpoint = 'fal-ai/veo3.1/reference-to-video';

-- fal-ai/veo3.1/first-last-frame-to-video
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "image_urls[0]",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "image_urls[0]",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "image_urls[1]",
    "type": "string",
    "default": "",
    "required": false,
    "mapping": "image_urls[1]",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 0,
      "max_duration": 8,
      "min_duration": 8
    },
    "default": 8,
    "required": true,
    "mapping": "duration",
    "mapping_type": "string",
    "notes": "Add s at the end of the duration"
  },
  {
    "key": "resolution",
    "type": "string",
    "accepted_values": ["720p", "1080p"],
    "default": "720p",
    "required": true,
    "mapping": "resolution",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["16:9"],
    "default": "16:9",
    "required": true,
    "mapping": "aspect_ratio",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "enable_audio",
    "type": "boolean",
    "default": false,
    "required": true,
    "mapping": "generate_audio",
    "mapping_type": "boolean",
    "notes": ""
  },
  {
    "key": "negative_prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "negative_prompt",
    "mapping_type": "string",
    "notes": "This is the negative prompt for the video"
  },
  {
    "default_values": {
      "auto_fix": true
    }
  }
]'::jsonb
WHERE endpoint = 'fal-ai/veo3.1/first-last-frame-to-video';

-- fal-ai/veo3.1/fast/first-last-frame-to-video
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "image_urls[0]",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "image_urls[0]",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "image_urls[1]",
    "type": "string",
    "default": "",
    "required": false,
    "mapping": "image_urls[1]",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 0,
      "max_duration": 8,
      "min_duration": 8
    },
    "default": 8,
    "required": true,
    "mapping": "duration",
    "mapping_type": "string",
    "notes": "Add s at the end of the duration"
  },
  {
    "key": "resolution",
    "type": "string",
    "accepted_values": ["720p", "1080p"],
    "default": "720p",
    "required": true,
    "mapping": "resolution",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["16:9"],
    "default": "16:9",
    "required": true,
    "mapping": "aspect_ratio",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "enable_audio",
    "type": "boolean",
    "default": false,
    "required": true,
    "mapping": "generate_audio",
    "mapping_type": "boolean",
    "notes": ""
  },
  {
    "key": "negative_prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "negative_prompt",
    "mapping_type": "string",
    "notes": "This is the negative prompt for the video"
  },
  {
    "default_values": {
      "auto_fix": true
    }
  }
]'::jsonb
WHERE endpoint = 'fal-ai/veo3.1/fast/first-last-frame-to-video';

-- fal-ai/veo3.1/image-to-video
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "image_url",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "image_url",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 2,
      "max_duration": 8,
      "min_duration": 4
    },
    "default": 4,
    "required": true,
    "mapping": "duration",
    "mapping_type": "string",
    "notes": "Add s at the end of the duration"
  },
  {
    "key": "resolution",
    "type": "string",
    "accepted_values": ["720p", "1080p"],
    "default": "1080p",
    "required": true,
    "mapping": "resolution",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["auto", "16:9", "9:16"],
    "default": "auto",
    "required": true,
    "mapping": "aspect_ratio",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "enable_audio",
    "type": "boolean",
    "required": true,
    "mapping": "generate_audio",
    "mapping_type": "boolean",
    "notes": ""
  },
  {
    "default_values": {
      "auto_fix": true
    }
  }
]'::jsonb
WHERE endpoint = 'fal-ai/veo3.1/image-to-video';

-- fal-ai/kling-video/v2.6/pro/image-to-video
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "image_url",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "image_url",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 5,
      "max_duration": 10,
      "min_duration": 5
    },
    "default": 5,
    "required": true,
    "mapping": "duration",
    "mapping_type": "integer",
    "notes": "Add s at the end of the duration"
  },
  {
    "key": "resolution",
    "type": "string",
    "accepted_values": ["1080p"],
    "default": "1080p",
    "required": true,
    "mapping": "resolution",
    "mapping_type": "string",
    "notes": "do not include the resolution in the payload"
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["1:1", "16:9", "9:16"],
    "default": "16:9",
    "required": true,
    "mapping": "aspect_ratio",
    "mapping_type": "string",
    "notes": "do not include the aspect ratio in the payload"
  },
  {
    "key": "negative_prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "negative_prompt",
    "mapping_type": "string",
    "notes": "This is the negative prompt for the video"
  },
  {
    "key": "enable_audio",
    "type": "boolean",
    "default": false,
    "required": true,
    "mapping": "generate_audio",
    "mapping_type": "boolean",
    "notes": ""
  }
]'::jsonb
WHERE endpoint = 'fal-ai/kling-video/v2.6/pro/image-to-video';

-- fal-ai/kling-video/v2.6/pro/text-to-video
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 5,
      "max_duration": 10,
      "min_duration": 5
    },
    "default": 5,
    "required": true,
    "mapping": "duration",
    "mapping_type": "integer",
    "notes": "Add s at the end of the duration"
  },
  {
    "key": "resolution",
    "type": "string",
    "accepted_values": ["1080p"],
    "default": "1080p",
    "required": true,
    "mapping": "resolution",
    "mapping_type": "string",
    "notes": "do not include the resolution in the payload"
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["1:1", "16:9", "9:16"],
    "default": "16:9",
    "required": true,
    "mapping": "aspect_ratio",
    "mapping_type": "string",
    "notes": "do not include the aspect ratio in the payload"
  },
  {
    "key": "negative_prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "negative_prompt",
    "mapping_type": "string",
    "notes": "This is the negative prompt for the video"
  },
  {
    "key": "enable_audio",
    "type": "boolean",
    "default": false,
    "required": true,
    "mapping": "generate_audio",
    "mapping_type": "boolean",
    "notes": ""
  }
]'::jsonb
WHERE endpoint = 'fal-ai/kling-video/v2.6/pro/text-to-video';

-- fal-ai/kling-video/o1/reference-to-video
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 5,
      "max_duration": 10,
      "min_duration": 5
    },
    "default": 5,
    "required": true,
    "mapping": "duration",
    "mapping_type": "integer",
    "notes": ""
  },
  {
    "key": "resolution",
    "type": "string",
    "accepted_values": ["1080p"],
    "default": "1080p",
    "required": true,
    "mapping": "resolution",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["1:1", "16:9", "9:16"],
    "default": "16:9",
    "required": true,
    "mapping": "aspect_ratio",
    "mapping_type": "string",
    "notes": "do not include the aspect ratio in the payload"
  },
  {
    "key": "elements[0].frontal_image_url",
    "type": "image",
    "default": "",
    "required": true,
    "mapping": "elements[0].frontal_image_url",
    "mapping_type": "image",
    "notes": "This is the main character front view"
  },
  {
    "key": "elements[0].reference_image_urls",
    "type": "image_array",
    "default": "",
    "required": false,
    "mapping": "elements[0].reference_image_urls",
    "mapping_type": "image_array",
    "notes": "This is the main character other angles"
  },
  {
    "key": "elements[1].frontal_image_url",
    "type": "image",
    "default": "",
    "required": false,
    "mapping": "elements[1].frontal_image_url",
    "mapping_type": "image",
    "notes": "This is the second character front view"
  },
  {
    "key": "elements[1].reference_image_urls",
    "type": "image_array",
    "default": "",
    "required": false,
    "mapping": "elements[1].reference_image_urls",
    "mapping_type": "image_array",
    "notes": "This is the second character other angles"
  },
  {
    "key": "image_urls[0]",
    "type": "image",
    "default": "",
    "required": false,
    "mapping": "image_urls[0]",
    "mapping_type": "image",
    "notes": "This is the style/look reference"
  },
  {
    "key": "image_urls[1]",
    "type": "image",
    "default": "",
    "required": false,
    "mapping": "image_urls[1]",
    "mapping_type": "image",
    "notes": "This is the background/environment"
  }
]'::jsonb
WHERE endpoint = 'fal-ai/kling-video/o1/reference-to-video';

-- fal-ai/sora-2/text-to-video/pro
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 4,
      "max_duration": 12,
      "min_duration": 4
    },
    "default": 4,
    "required": true,
    "mapping": "duration",
    "mapping_type": "integer",
    "notes": "Add s at the end of the duration"
  },
  {
    "key": "resolution",
    "type": "string",
    "accepted_values": ["720p", "1080p"],
    "default": "1080p",
    "required": true,
    "mapping": "resolution",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["16:9", "9:16"],
    "default": "16:9",
    "required": true,
    "mapping": "aspect_ratio",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "default_values": {
      "delete_video": true
    }
  }
]'::jsonb
WHERE endpoint = 'fal-ai/sora-2/text-to-video/pro';

-- fal-ai/sora-2/text-to-video
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 4,
      "max_duration": 12,
      "min_duration": 4
    },
    "default": 4,
    "required": true,
    "mapping": "duration",
    "mapping_type": "integer",
    "notes": "Add s at the end of the duration"
  },
  {
    "key": "resolution",
    "type": "string",
    "accepted_values": ["720p"],
    "default": "720p",
    "required": true,
    "mapping": "resolution",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["16:9", "9:16"],
    "default": "16:9",
    "required": true,
    "mapping": "aspect_ratio",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "default_values": {
      "delete_video": true
    }
  }
]'::jsonb
WHERE endpoint = 'fal-ai/sora-2/text-to-video';

-- fal-ai/sora-2/image-to-video
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "image_url",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "image_url",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 4,
      "max_duration": 12,
      "min_duration": 4
    },
    "default": 4,
    "required": true,
    "mapping": "duration",
    "mapping_type": "integer",
    "notes": "Add s at the end of the duration"
  },
  {
    "key": "resolution",
    "type": "string",
    "accepted_values": ["720p"],
    "default": "720p",
    "required": true,
    "mapping": "resolution",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["16:9", "9:16", "auto"],
    "default": "auto",
    "required": true,
    "mapping": "aspect_ratio",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "default_values": {
      "delete_video": true
    }
  }
]'::jsonb
WHERE endpoint = 'fal-ai/sora-2/image-to-video';

-- fal-ai/sora-2/image-to-video/pro
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "image_url",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "image_url",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 4,
      "max_duration": 12,
      "min_duration": 4
    },
    "default": 4,
    "required": true,
    "mapping": "duration",
    "mapping_type": "integer",
    "notes": "Add s at the end of the duration"
  },
  {
    "key": "resolution",
    "type": "string",
    "accepted_values": ["720p", "1080p"],
    "default": "1080p",
    "required": true,
    "mapping": "resolution",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["16:9", "9:16", "auto"],
    "default": "auto",
    "required": true,
    "mapping": "aspect_ratio",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "default_values": {
      "delete_video": true
    }
  }
]'::jsonb
WHERE endpoint = 'fal-ai/sora-2/image-to-video/pro';

-- fal-ai/sora-2/video-to-video/remix
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "video_url",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "video_url",
    "mapping_type": "string",
    "notes": ""
  }
]'::jsonb
WHERE endpoint = 'fal-ai/sora-2/video-to-video/remix';

-- fal-ai/ltx-2/text-to-video
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "fps",
    "type": "integer",
    "accepted_values": [25, 50],
    "default": 25,
    "required": true,
    "mapping": "fps",
    "mapping_type": "integer",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 2,
      "max_duration": 10,
      "min_duration": 6
    },
    "default": 6,
    "required": true,
    "mapping": "duration",
    "mapping_type": "integer",
    "notes": "Add s at the end of the duration"
  },
  {
    "key": "resolution",
    "type": "string",
    "accepted_values": ["1080p", "1440p", "2160p"],
    "default": "1080p",
    "required": true,
    "mapping": "resolution",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["16:9"],
    "default": "16:9",
    "required": true,
    "mapping": "aspect_ratio",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "enable_audio",
    "type": "boolean",
    "default": false,
    "required": true,
    "mapping": "generate_audio",
    "mapping_type": "boolean",
    "notes": ""
  }
]'::jsonb
WHERE endpoint = 'fal-ai/ltx-2/text-to-video';

-- fal-ai/ltx-2/image-to-video
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "image_url",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "image_url",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "fps",
    "type": "integer",
    "accepted_values": [25, 50],
    "default": 25,
    "required": true,
    "mapping": "fps",
    "mapping_type": "integer",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 2,
      "max_duration": 10,
      "min_duration": 6
    },
    "default": 6,
    "required": true,
    "mapping": "duration",
    "mapping_type": "integer",
    "notes": "Add s at the end of the duration"
  },
  {
    "key": "resolution",
    "type": "string",
    "accepted_values": ["1080p", "1440p", "2160p"],
    "default": "1080p",
    "required": true,
    "mapping": "resolution",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["16:9"],
    "default": "16:9",
    "required": true,
    "mapping": "aspect_ratio",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "enable_audio",
    "type": "boolean",
    "default": false,
    "required": true,
    "mapping": "generate_audio",
    "mapping_type": "boolean",
    "notes": ""
  }
]'::jsonb
WHERE endpoint = 'fal-ai/ltx-2/image-to-video';

-- fal-ai/ltx-2/text-to-video/fast
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "fps",
    "type": "integer",
    "accepted_values": [25, 50],
    "default": 25,
    "required": true,
    "mapping": "fps",
    "mapping_type": "integer",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 2,
      "max_duration": 20,
      "min_duration": 6
    },
    "default": 6,
    "required": true,
    "mapping": "duration",
    "mapping_type": "integer",
    "notes": "Add s at the end of the duration"
  },
  {
    "key": "resolution",
    "type": "string",
    "accepted_values": ["1080p", "1440p", "2160p"],
    "default": "1080p",
    "required": true,
    "mapping": "resolution",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["16:9"],
    "default": "16:9",
    "required": true,
    "mapping": "aspect_ratio",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "enable_audio",
    "type": "boolean",
    "default": false,
    "required": true,
    "mapping": "generate_audio",
    "mapping_type": "boolean",
    "notes": ""
  }
]'::jsonb
WHERE endpoint = 'fal-ai/ltx-2/text-to-video/fast';

-- fal-ai/ltx-2/image-to-video/fast
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "image_url",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "image_url",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "fps",
    "type": "integer",
    "accepted_values": [25, 50],
    "default": 25,
    "required": true,
    "mapping": "fps",
    "mapping_type": "integer",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 2,
      "max_duration": 20,
      "min_duration": 6
    },
    "default": 6,
    "required": true,
    "mapping": "duration",
    "mapping_type": "integer",
    "notes": "Add s at the end of the duration"
  },
  {
    "key": "resolution",
    "type": "string",
    "accepted_values": ["1080p", "1440p", "2160p"],
    "default": "1080p",
    "required": true,
    "mapping": "resolution",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["16:9"],
    "default": "16:9",
    "required": true,
    "mapping": "aspect_ratio",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "enable_audio",
    "type": "boolean",
    "default": false,
    "required": true,
    "mapping": "generate_audio",
    "mapping_type": "boolean",
    "notes": ""
  }
]'::jsonb
WHERE endpoint = 'fal-ai/ltx-2/image-to-video/fast';

-- fal-ai/ltx-2/retake-video
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 1,
      "max_duration": 20,
      "min_duration": 2
    },
    "default": 2,
    "required": true,
    "mapping": "duration",
    "mapping_type": "integer",
    "notes": "Add s at the end of the duration"
  },
  {
    "key": "retake_mode",
    "type": "string",
    "accepted_values": ["replace_audio", "replace_video", "replace_audio_and_video"],
    "default": "replace_audio",
    "required": true,
    "mapping": "retake_mode",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["16:9"],
    "default": "16:9",
    "required": true,
    "mapping": "aspect_ratio",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "video_url",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "video_url",
    "mapping_type": "string",
    "notes": ""
  }
]'::jsonb
WHERE endpoint = 'fal-ai/ltx-2/retake-video';

-- fal-ai/minimax/speech-2.6-hd
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "text",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "text",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "voice",
    "type": "string",
    "accepted_values": [
      "Lovely_Girl",
      "Decent_Boy",
      "Imposing_Manner",
      "Elegant_Man",
      "Abbess",
      "Sweet_Girl_2",
      "Exuberant_Girl",
      "Wise_Woman",
      "Friendly_Person",
      "Inspirational_girl",
      "Deep_Voice_Man",
      "Calm_Woman",
      "Casual_Guy",
      "Lively_Girl",
      "Patient_Man",
      "Young_Knight",
      "Determined_Man"
    ],
    "default": "Lovely_Girl",
    "required": true,
    "mapping": "voice_id",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "speech_speed",
    "type": "float",
    "accepted_values": {
      "steps": 0.1,
      "max_speed": 2,
      "min_speed": 0.5
    },
    "default": 1.0,
    "required": false,
    "mapping": "speed",
    "mapping_type": "float",
    "notes": ""
  },
  {
    "key": "voice_emotion",
    "type": "string",
    "accepted_values": ["happy", "sad", "angry", "fearful", "disgusted", "surprised", "neutral"],
    "default": "neutral",
    "required": false,
    "mapping": "emotion",
    "mapping_type": "string",
    "notes": ""
  }
]'::jsonb
WHERE endpoint = 'fal-ai/minimax/speech-2.6-hd';

-- beatoven/sound-effect-generation
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 1,
      "max_duration": 35,
      "min_duration": 1
    },
    "default": 5,
    "required": true,
    "mapping": "duration",
    "mapping_type": "integer",
    "notes": ""
  },
  {
    "key": "negative_prompt",
    "type": "string",
    "default": "",
    "required": false,
    "mapping": "negative_prompt",
    "mapping_type": "string",
    "notes": ""
  }
]'::jsonb
WHERE endpoint = 'beatoven/sound-effect-generation';

-- fal-ai/kling-video/video-to-audio
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "video_url",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "video_url",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "background_music_prompt",
    "type": "string",
    "default": "",
    "required": false,
    "mapping": "background_music_prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "asmr_mode",
    "type": "boolean",
    "default": false,
    "required": false,
    "mapping": "asmr_mode",
    "mapping_type": "boolean",
    "notes": ""
  }
]'::jsonb
WHERE endpoint = 'fal-ai/kling-video/video-to-audio';

-- argil/avatars/text-to-video
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "avatar",
    "type": "string",
    "accepted_values": [
      "Lara (Masterclass)",
      "Maria (Masterclass)",
      "Sienna (Masterclass)",
      "Jasmine (Masterclass)",
      "Amara (Masterclass)",
      "Tyler (Masterclass)",
      "Jayse (Masterclass)",
      "Paul (Masterclass)",
      "Viva (Masterclass)",
      "Alex (Masterclass)",
      "Byron (Masterclass)",
      "Calista (Masterclass)",
      "Fabien (Masterclass)",
      "Laurent (UGC)",
      "Noemie car (UGC)"
    ],
    "default": "Lara (Masterclass)",
    "required": true,
    "mapping": "avatar",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "transparent_background",
    "type": "boolean",
    "default": false,
    "required": false,
    "mapping": "remove_background",
    "mapping_type": "boolean",
    "notes": ""
  }
]'::jsonb
WHERE endpoint = 'argil/avatars/text-to-video';

-- fal-ai/mmaudio-v2
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "video_url",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "video_url",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 1,
      "max_duration": 30,
      "min_duration": 1
    },
    "default": 10,
    "required": false,
    "mapping": "duration",
    "mapping_type": "integer",
    "notes": ""
  }
]'::jsonb
WHERE endpoint = 'fal-ai/mmaudio-v2';

-- beatoven/music-generation
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 1,
      "max_duration": 150,
      "min_duration": 1
    },
    "default": 30,
    "required": true,
    "mapping": "duration",
    "mapping_type": "integer",
    "notes": ""
  },
  {
    "key": "negative_prompt",
    "type": "string",
    "default": "",
    "required": false,
    "mapping": "negative_prompt",
    "mapping_type": "string",
    "notes": ""
  }
]'::jsonb
WHERE endpoint = 'beatoven/music-generation';

-- fal-ai/gpt-image-1-mini
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "background",
    "type": "string",
    "accepted_values": ["auto", "transparent", "opaque"],
    "default": "auto",
    "required": false,
    "mapping": "background",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "resolution",
    "type": "string",
    "accepted_values": ["auto", "low", "medium", "high"],
    "default": "auto",
    "required": false,
    "mapping": "quality",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["auto", "1024x1024", "1024x1536", "1536x1024"],
    "default": "auto",
    "required": false,
    "mapping": "size",
    "mapping_type": "string",
    "notes": ""
  }
]'::jsonb
WHERE endpoint = 'fal-ai/gpt-image-1-mini';

-- mirelo-ai/sfx-v1.5/video-to-audio
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "video_url",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "video_url",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 1,
      "max_duration": 10,
      "min_duration": 1
    },
    "default": 5,
    "required": false,
    "mapping": "duration",
    "mapping_type": "integer",
    "notes": ""
  }
]'::jsonb
WHERE endpoint = 'mirelo-ai/sfx-v1.5/video-to-audio';

-- fal-ai/minimax/hailuo-2.3/standard/text-to-video
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 4,
      "max_duration": 10,
      "min_duration": 6
    },
    "default": 6,
    "required": true,
    "mapping": "duration",
    "mapping_type": "string",
    "notes": "Value type is string"
  },
  {
    "key": "resolution",
    "type": "string",
    "accepted_values": ["768p"],
    "default": "768p",
    "required": true,
    "mapping": "resolution",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["16:9"],
    "default": "16:9",
    "required": true,
    "mapping": "aspect_ratio",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "enhance_prompt",
    "type": "boolean",
    "default": false,
    "required": false,
    "mapping": "prompt_optimizer",
    "mapping_type": "boolean",
    "notes": ""
  }
]'::jsonb
WHERE endpoint = 'fal-ai/minimax/hailuo-2.3/standard/text-to-video';

-- fal-ai/stable-audio-25/text-to-audio
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 1,
      "max_duration": 190,
      "min_duration": 1
    },
    "default": 30,
    "required": true,
    "mapping": "seconds_total",
    "mapping_type": "integer",
    "notes": ""
  }
]'::jsonb
WHERE endpoint = 'fal-ai/stable-audio-25/text-to-audio';

-- fal-ai/kling-video/ai-avatar/v2/pro
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": false,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "image_url",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "image_url",
    "mapping_type": "string",
    "notes": "Avatar image"
  },
  {
    "key": "audio_url",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "audio_url",
    "mapping_type": "string",
    "notes": "Audio file for lip sync"
  }
]'::jsonb
WHERE endpoint = 'fal-ai/kling-video/ai-avatar/v2/pro';

-- fal-ai/kling-video/v1/tts
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "text",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "text",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "voice",
    "type": "string",
    "accepted_values": [
      "genshin_vindi2",
      "zhinen_xuesheng",
      "AOT",
      "ai_shatang",
      "genshin_klee2",
      "genshin_kirara",
      "ai_kaiya",
      "oversea_male1",
      "ai_chenjiahao_712",
      "girlfriend_4_speech02",
      "chat1_female_new-3",
      "chat_0407_5-1",
      "cartoon-boy-07",
      "uk_boy1",
      "cartoon-girl-01",
      "PeppaPig_platform",
      "ai_huangzhong_712",
      "ai_huangyaoshi_712",
      "ai_laoguowang_712",
      "chengshu_jiejie",
      "you_pingjing",
      "calm_story1",
      "uk_man2",
      "laopopo_speech02",
      "heainainai_speech02",
      "reader_en_m-v1",
      "commercial_lady_en_f-v1",
      "tiyuxi_xuedi",
      "tiexin_nanyou",
      "girlfriend_1_speech02",
      "girlfriend_2_speech02",
      "zhuxi_speech02",
      "uk_oldman3",
      "dongbeilaotie_speech02",
      "chongqingxiaohuo_speech02",
      "chuanmeizi_speech02",
      "chaoshandashu_speech02",
      "ai_taiwan_man2_speech02",
      "xianzhanggui_speech02",
      "tianjinjiejie_speech02",
      "diyinnansang_DB_CN_M_04-v2",
      "yizhipiannan-v1",
      "guanxiaofang-v2",
      "tianmeixuemei-v1",
      "daopianyansang-v1",
      "mengwa-v1"
    ],
    "default": "oversea_male1",
    "required": true,
    "mapping": "voice_id",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "speech_speed",
    "type": "float",
    "accepted_values": {
      "steps": 0.1,
      "max_speed": 2,
      "min_speed": 0.8
    },
    "default": 1.0,
    "required": false,
    "mapping": "voice_speed",
    "mapping_type": "float",
    "notes": ""
  }
]'::jsonb
WHERE endpoint = 'fal-ai/kling-video/v1/tts';

-- fal-ai/minimax/hailuo-2.3/standard/image-to-video
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "image_url",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "image_url",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 4,
      "max_duration": 10,
      "min_duration": 6
    },
    "default": 6,
    "required": true,
    "mapping": "duration",
    "mapping_type": "string",
    "notes": "Value type is string"
  },
  {
    "key": "resolution",
    "type": "string",
    "accepted_values": ["768p"],
    "default": "768p",
    "required": true,
    "mapping": "resolution",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["16:9"],
    "default": "16:9",
    "required": true,
    "mapping": "aspect_ratio",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "enhance_prompt",
    "type": "boolean",
    "default": false,
    "required": false,
    "mapping": "prompt_optimizer",
    "mapping_type": "boolean",
    "notes": ""
  }
]'::jsonb
WHERE endpoint = 'fal-ai/minimax/hailuo-2.3/standard/image-to-video';

-- fal-ai/minimax/speech-2.6-turbo
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "text",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "text",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "voice",
    "type": "string",
    "accepted_values": [
      "Lovely_Girl",
      "Decent_Boy",
      "Imposing_Manner",
      "Elegant_Man",
      "Abbess",
      "Sweet_Girl_2",
      "Exuberant_Girl",
      "Wise_Woman",
      "Friendly_Person",
      "Inspirational_girl",
      "Deep_Voice_Man",
      "Calm_Woman",
      "Casual_Guy",
      "Lively_Girl",
      "Patient_Man",
      "Young_Knight",
      "Determined_Man"
    ],
    "default": "Lovely_Girl",
    "required": true,
    "mapping": "voice_id",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "speech_speed",
    "type": "float",
    "accepted_values": {
      "steps": 0.1,
      "max_speed": 2,
      "min_speed": 0.5
    },
    "default": 1.0,
    "required": false,
    "mapping": "speed",
    "mapping_type": "float",
    "notes": ""
  },
  {
    "key": "voice_emotion",
    "type": "string",
    "accepted_values": ["happy", "sad", "angry", "fearful", "disgusted", "surprised", "neutral"],
    "default": "neutral",
    "required": false,
    "mapping": "emotion",
    "mapping_type": "string",
    "notes": ""
  }
]'::jsonb
WHERE endpoint = 'fal-ai/minimax/speech-2.6-turbo';

-- fal-ai/minimax/hailuo-2.3/pro/text-to-video
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 0,
      "max_duration": 6,
      "min_duration": 6
    },
    "default": 6,
    "required": true,
    "mapping": "duration",
    "mapping_type": "string",
    "notes": "Fixed at 6 seconds"
  },
  {
    "key": "resolution",
    "type": "string",
    "accepted_values": ["1080p"],
    "default": "1080p",
    "required": true,
    "mapping": "resolution",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["16:9"],
    "default": "16:9",
    "required": true,
    "mapping": "aspect_ratio",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "enhance_prompt",
    "type": "boolean",
    "default": false,
    "required": false,
    "mapping": "prompt_optimizer",
    "mapping_type": "boolean",
    "notes": ""
  }
]'::jsonb
WHERE endpoint = 'fal-ai/minimax/hailuo-2.3/pro/text-to-video';

-- fal-ai/mmaudio-v2/text-to-audio
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 1,
      "max_duration": 30,
      "min_duration": 1
    },
    "default": 10,
    "required": true,
    "mapping": "duration",
    "mapping_type": "integer",
    "notes": ""
  }
]'::jsonb
WHERE endpoint = 'fal-ai/mmaudio-v2/text-to-audio';

-- fal-ai/nano-banana-pro
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "resolution",
    "type": "string",
    "accepted_values": ["1K", "2K", "4K"],
    "default": "2K",
    "required": false,
    "mapping": "resolution",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["21:9", "16:9", "3:2", "4:3", "5:4", "1:1", "4:5", "3:4", "2:3", "9:16"],
    "default": "16:9",
    "required": false,
    "mapping": "aspect_ratio",
    "mapping_type": "string",
    "notes": ""
  }
]'::jsonb
WHERE endpoint = 'fal-ai/nano-banana-pro';

-- fal-ai/minimax/hailuo-2.3-fast/standard/image-to-video
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "image_url",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "image_url",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 4,
      "max_duration": 10,
      "min_duration": 6
    },
    "default": 6,
    "required": true,
    "mapping": "duration",
    "mapping_type": "string",
    "notes": "Value type is string"
  },
  {
    "key": "resolution",
    "type": "string",
    "accepted_values": ["768p"],
    "default": "768p",
    "required": true,
    "mapping": "resolution",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["16:9"],
    "default": "16:9",
    "required": true,
    "mapping": "aspect_ratio",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "enhance_prompt",
    "type": "boolean",
    "default": false,
    "required": false,
    "mapping": "prompt_optimizer",
    "mapping_type": "boolean",
    "notes": ""
  }
]'::jsonb
WHERE endpoint = 'fal-ai/minimax/hailuo-2.3-fast/standard/image-to-video';

-- sonauto/v2/text-to-music
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  }
]'::jsonb
WHERE endpoint = 'sonauto/v2/text-to-music';

-- fal-ai/minimax/hailuo-2.3/pro/image-to-video
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "image_url",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "image_url",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 0,
      "max_duration": 6,
      "min_duration": 6
    },
    "default": 6,
    "required": true,
    "mapping": "duration",
    "mapping_type": "string",
    "notes": "Fixed at 6 seconds"
  },
  {
    "key": "resolution",
    "type": "string",
    "accepted_values": ["1080p"],
    "default": "1080p",
    "required": true,
    "mapping": "resolution",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["16:9"],
    "default": "16:9",
    "required": true,
    "mapping": "aspect_ratio",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "enhance_prompt",
    "type": "boolean",
    "default": false,
    "required": false,
    "mapping": "prompt_optimizer",
    "mapping_type": "boolean",
    "notes": ""
  }
]'::jsonb
WHERE endpoint = 'fal-ai/minimax/hailuo-2.3/pro/image-to-video';

-- fal-ai/kling-video/ai-avatar/v2/standard
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": false,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "image_url",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "image_url",
    "mapping_type": "string",
    "notes": "Avatar image"
  },
  {
    "key": "audio_url",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "audio_url",
    "mapping_type": "string",
    "notes": "Audio file for lip sync"
  }
]'::jsonb
WHERE endpoint = 'fal-ai/kling-video/ai-avatar/v2/standard';

-- fal-ai/minimax/hailuo-2.3-fast/pro/image-to-video
UPDATE octupost.ai_providers SET parameters = '[
  {
    "key": "prompt",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "prompt",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "image_url",
    "type": "string",
    "default": "",
    "required": true,
    "mapping": "image_url",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "duration",
    "type": "integer",
    "accepted_values": {
      "steps": 0,
      "max_duration": 6,
      "min_duration": 6
    },
    "default": 6,
    "required": true,
    "mapping": "duration",
    "mapping_type": "string",
    "notes": "Fixed at 6 seconds"
  },
  {
    "key": "resolution",
    "type": "string",
    "accepted_values": ["1080p"],
    "default": "1080p",
    "required": true,
    "mapping": "resolution",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "aspect_ratio",
    "type": "string",
    "accepted_values": ["16:9"],
    "default": "16:9",
    "required": true,
    "mapping": "aspect_ratio",
    "mapping_type": "string",
    "notes": ""
  },
  {
    "key": "enhance_prompt",
    "type": "boolean",
    "default": false,
    "required": false,
    "mapping": "prompt_optimizer",
    "mapping_type": "boolean",
    "notes": ""
  }
]'::jsonb
WHERE endpoint = 'fal-ai/minimax/hailuo-2.3-fast/pro/image-to-video';

COMMIT;

-- =============================================================================
-- END OF MIGRATION
-- =============================================================================
-- Total endpoints updated: 47
-- 
-- To verify the migration, run:
--   SELECT endpoint, parameters FROM octupost.ai_providers 
--   WHERE endpoint LIKE 'fal-ai/%' OR endpoint LIKE 'beatoven/%' 
--   OR endpoint LIKE 'argil/%' OR endpoint LIKE 'mirelo-ai/%' 
--   OR endpoint LIKE 'sonauto/%';
-- =============================================================================

