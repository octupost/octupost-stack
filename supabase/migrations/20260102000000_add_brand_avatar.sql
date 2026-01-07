-- Add avatar fields to brand_kits table
ALTER TABLE octupost.brand_kits
ADD COLUMN IF NOT EXISTS avatar_url TEXT,
ADD COLUMN IF NOT EXISTS avatar_style TEXT;

-- Add comments for documentation
COMMENT ON COLUMN octupost.brand_kits.avatar_url IS 'URL of brand avatar/mascot image';
COMMENT ON COLUMN octupost.brand_kits.avatar_style IS 'Avatar style: realistic, cartoon, 3d, minimalist, illustrated';
