import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
One mor question 
// Types
interface AssetPayload {
  asset_id: string;
  url: string;
  type: "video" | "audio" | "speech" | "image";
}

interface FalMetadataResponse {
  streams: Array<{
    codec_type: string;
    codec_name: string;
    width?: number;
    height?: number;
    duration?: string;
    sample_rate?: string;
    channels?: number;
    bit_rate?: string;
    r_frame_rate?: string;
  }>;
  format: {
    duration?: string;
    bit_rate?: string;
    format_name?: string;
  };
  frames?: Array<{
    url: string;
    content_type?: string;
    width?: number;
    height?: number;
  }>;
}

// Twelve Labs API response structure
interface TwelveLabsSegment {
  start_offset_time?: number;
  end_offset_time?: number;
  embedding_scope?: string;
  float: number[];
}

interface TwelveLabsEmbedResponse {
  segments?: TwelveLabsSegment[];
  // For images, the response structure might be different
  embedding?: {
    float: number[];
  };
}

// Helper to call fal.ai API (synchronous endpoint)
async function callFalApi<T>(endpoint: string, input: Record<string, unknown>): Promise<T> {
  const FAL_KEY = Deno.env.get("FAL_KEY");
  if (!FAL_KEY) {
    throw new Error("FAL_KEY environment variable not set");
  }

  // Use synchronous endpoint (fal.run) instead of queue endpoint
  const response = await fetch(`https://fal.run/${endpoint}`, {
    method: "POST",
    headers: {
      "Authorization": `Key ${FAL_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input), // Send input directly, not wrapped
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`fal.ai API error: ${response.status} - ${error}`);
  }

  return await response.json() as T;
}

// Extract metadata using fal.ai ffprobe
// For videos: extract_frames = true, for other types: extract_frames = false
async function extractMetadata(url: string, type: AssetPayload["type"]): Promise<FalMetadataResponse> {
  return await callFalApi<FalMetadataResponse>("fal-ai/ffmpeg-api/metadata", {
    media_url: url,
    extract_frames: type === "video",
  });
}

// Generate embedding using Twelve Labs API
async function generateEmbedding(url: string, type: AssetPayload["type"]): Promise<number[] | null> {
  const TWELVELABS_API_KEY = Deno.env.get("TWELVELABS_API_KEY");
  if (!TWELVELABS_API_KEY) {
    console.warn("TWELVELABS_API_KEY not set, skipping embedding generation");
    return null;
  }

  // Build request body based on asset type
  const body: Record<string, string> = {
    model_name: "Marengo-retrieval-2.7",
  };

  if (type === "image") {
    body.image_url = url;
  } else if (type === "video") {
    body.video_url = url;
  } else {
    // audio, speech
    body.audio_url = url;
  }

  console.log(`Generating embedding for ${type} asset using Twelve Labs...`);
  console.log(`Request body: ${JSON.stringify(body)}`);

  const response = await fetch("https://api.twelvelabs.io/v1.3/embed-v2", {
    method: "POST",
    headers: {
      "x-api-key": TWELVELABS_API_KEY,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Twelve Labs API error: ${response.status} - ${error}`);
  }

  const result = await response.json() as TwelveLabsEmbedResponse;
  console.log(`Twelve Labs response keys: ${Object.keys(result).join(", ")}`);
  
  // Try to extract embedding from response
  // For video/audio: response.segments[0].float
  // For images: response.embedding.float or response.segments[0].float
  let embeddingArray: number[] | null = null;
  
  if (result.segments && result.segments.length > 0 && result.segments[0].float) {
    embeddingArray = result.segments[0].float;
    console.log(`Embedding extracted from segments, dimensions: ${embeddingArray.length}`);
  } else if (result.embedding?.float) {
    embeddingArray = result.embedding.float;
    console.log(`Embedding extracted from embedding.float, dimensions: ${embeddingArray.length}`);
  } else {
    console.error(`Unexpected response structure: ${JSON.stringify(result).slice(0, 500)}`);
  }
  
  return embeddingArray;
}

// Main handler
Deno.serve(async (req: Request) => {
  // Handle CORS preflight
  if (req.method === "OPTIONS") {
    return new Response(null, {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
      },
    });
  }

  try {
    // Parse request body
    const payload: AssetPayload = await req.json();
    const { asset_id, url, type } = payload;

    console.log(`Processing asset ${asset_id} of type ${type}`);

    if (!asset_id || !url || !type) {
      return new Response(
        JSON.stringify({ error: "Missing required fields: asset_id, url, type" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    // Initialize Supabase client with service role and octupost schema
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const supabase = createClient(supabaseUrl, supabaseServiceKey, {
      db: {
        schema: 'octupost'  // Use the octupost schema
      }
    });

    let metadata: FalMetadataResponse | { extraction_failed: boolean; error: string };
    let embedding: number[] | null = null;

    // Step 1: Extract metadata using fal.ai
    try {
      console.log(`Extracting metadata from ${url} with extract_frames=${type === "video"}`);
      metadata = await extractMetadata(url, type);
      console.log("Raw metadata:", JSON.stringify(metadata));
    } catch (extractionError) {
      console.error("Metadata extraction failed:", extractionError);
      metadata = {
        extraction_failed: true,
        error: extractionError instanceof Error ? extractionError.message : String(extractionError),
      };
    }

    // Step 2: Generate embedding using Twelve Labs
    try {
      embedding = await generateEmbedding(url, type);
      if (embedding) {
        console.log(`Embedding generated with ${embedding.length} dimensions`);
      } else {
        console.warn("No embedding returned from Twelve Labs");
      }
    } catch (embeddingError) {
      console.error("Embedding generation failed:", embeddingError);
      // Don't fail the whole request if embedding fails - metadata is still valuable
    }

    // Step 3: Update asset in database with metadata and embedding
    // Build update object - only include embedding if it was generated
    const updateData: Record<string, unknown> = {
      metadata: metadata,
      updated_at_utc: new Date().toISOString(),
    };

    if (embedding && embedding.length > 0) {
      // Convert array to pgvector format string: [x,y,z,...]
      updateData.embedding = `[${embedding.join(",")}]`;
      console.log(`Setting embedding with ${embedding.length} dimensions`);
    }

    const { error: updateError } = await supabase
      .from("assets")
      .update(updateData)
      .eq("id", asset_id)
      .single();

    if (updateError) {
      console.error("Failed to update asset:", updateError);
      return new Response(
        JSON.stringify({ error: "Failed to update asset", details: updateError }),
        { status: 500, headers: { "Content-Type": "application/json" } }
      );
    }

    console.log(`Successfully processed asset ${asset_id} (embedding: ${embedding ? "yes" : "no"})`);

    return new Response(
      JSON.stringify({
        success: true,
        asset_id,
        metadata: metadata,
        embedding_generated: !!embedding,
        embedding_dimensions: embedding?.length || 0,
      }),
      {
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
        },
      }
    );

  } catch (error) {
    console.error("Edge function error:", error);
    return new Response(
      JSON.stringify({
        error: "Internal server error",
        details: error instanceof Error ? error.message : String(error),
      }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      }
    );
  }
});
