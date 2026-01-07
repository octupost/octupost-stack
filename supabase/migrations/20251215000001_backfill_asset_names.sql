-- Backfill names for existing assets
-- This migration generates user-friendly names based on available data:
-- 1. AI-generated: First 5 words from prompt
-- 2. Uploads: Cleaned filename from metadata
-- 3. URL imports: Filename extracted from URL
-- 4. Fallback: Type + creation date

BEGIN;

-- Create a helper function to extract prompt excerpt (first N words)
CREATE OR REPLACE FUNCTION pg_temp.extract_prompt_excerpt(prompt TEXT, max_words INT DEFAULT 5)
RETURNS TEXT AS $$
DECLARE
  words TEXT[];
  result TEXT;
BEGIN
  IF prompt IS NULL OR prompt = '' THEN
    RETURN NULL;
  END IF;
  
  -- Split by whitespace and take first N words
  words := string_to_array(regexp_replace(trim(prompt), '\s+', ' ', 'g'), ' ');
  result := array_to_string(words[1:max_words], ' ');
  
  -- Capitalize first letter
  IF length(result) > 0 THEN
    result := upper(substring(result, 1, 1)) || substring(result, 2);
  END IF;
  
  -- Truncate to 50 chars
  IF length(result) > 50 THEN
    result := substring(result, 1, 49) || '…';
  END IF;
  
  RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Create a helper function to clean filename
CREATE OR REPLACE FUNCTION pg_temp.clean_filename(filename TEXT)
RETURNS TEXT AS $$
DECLARE
  result TEXT;
BEGIN
  IF filename IS NULL OR filename = '' THEN
    RETURN NULL;
  END IF;
  
  result := filename;
  
  -- Remove extension
  result := regexp_replace(result, '\.[^.]+$', '');
  
  -- Remove timestamp prefixes (10-13 digits followed by dash)
  result := regexp_replace(result, '^\d{10,13}-', '');
  
  -- Remove UUID prefixes
  result := regexp_replace(result, '^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}-?', '', 'i');
  
  -- Replace underscores and dashes with spaces
  result := regexp_replace(result, '[_-]', ' ', 'g');
  
  -- Split camelCase
  result := regexp_replace(result, '([a-z])([A-Z])', '\1 \2', 'g');
  
  -- Clean up multiple spaces
  result := regexp_replace(trim(result), '\s+', ' ', 'g');
  
  -- Return null if result is empty or just numbers
  IF result = '' OR result ~ '^\d+$' THEN
    RETURN NULL;
  END IF;
  
  -- Truncate to 50 chars
  IF length(result) > 50 THEN
    result := substring(result, 1, 49) || '…';
  END IF;
  
  RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Create a helper function to extract filename from URL
CREATE OR REPLACE FUNCTION pg_temp.extract_filename_from_url(url TEXT)
RETURNS TEXT AS $$
DECLARE
  path_part TEXT;
  segments TEXT[];
  last_segment TEXT;
  cleaned TEXT;
BEGIN
  IF url IS NULL OR url = '' THEN
    RETURN NULL;
  END IF;
  
  -- Extract path from URL (after domain)
  path_part := regexp_replace(url, '^https?://[^/]+', '');
  
  -- Split by / and get last non-empty segment
  segments := string_to_array(path_part, '/');
  last_segment := NULL;
  
  FOR i IN REVERSE array_length(segments, 1)..1 LOOP
    IF segments[i] IS NOT NULL AND segments[i] != '' THEN
      last_segment := segments[i];
      EXIT;
    END IF;
  END LOOP;
  
  IF last_segment IS NULL THEN
    RETURN NULL;
  END IF;
  
  -- Check if it looks like a filename (has extension)
  IF last_segment !~ '\.[a-zA-Z0-9]{2,5}$' THEN
    RETURN NULL;
  END IF;
  
  -- URL decode (basic)
  last_segment := regexp_replace(last_segment, '%20', ' ', 'g');
  last_segment := regexp_replace(last_segment, '%2F', '/', 'g');
  
  -- Clean the filename
  cleaned := pg_temp.clean_filename(last_segment);
  
  -- Check if result is meaningful (not just hash)
  IF cleaned IS NULL OR cleaned ~ '^[a-f0-9]+$' THEN
    RETURN NULL;
  END IF;
  
  RETURN cleaned;
END;
$$ LANGUAGE plpgsql;

-- Update all assets that don't have a name yet
UPDATE octupost.assets
SET name = COALESCE(
  -- 1. For AI-generated: use prompt
  CASE 
    WHEN source = 'generative_ai' AND generation_params->>'prompt' IS NOT NULL 
    THEN pg_temp.extract_prompt_excerpt(generation_params->>'prompt', 5)
    ELSE NULL
  END,
  
  -- 2. For uploads: use filename from metadata
  CASE 
    WHEN source = 'local_upload' AND metadata->>'filename' IS NOT NULL 
    THEN pg_temp.clean_filename(metadata->>'filename')
    ELSE NULL
  END,
  
  -- 3. For URL imports: try to extract from URL
  CASE 
    WHEN source = 'public_url' AND url IS NOT NULL 
    THEN pg_temp.extract_filename_from_url(url)
    ELSE NULL
  END,
  
  -- 4. Also try filename from metadata regardless of source
  CASE 
    WHEN metadata->>'filename' IS NOT NULL 
    THEN pg_temp.clean_filename(metadata->>'filename')
    ELSE NULL
  END,
  
  -- 5. Also try extracting from URL regardless of source
  CASE 
    WHEN url IS NOT NULL 
    THEN pg_temp.extract_filename_from_url(url)
    ELSE NULL
  END,
  
  -- 6. Fallback: Type + creation date
  initcap(type::text) || ' - ' || to_char(COALESCE(created_at_utc, NOW()), 'Mon DD')
)
WHERE name IS NULL;

COMMIT;
















