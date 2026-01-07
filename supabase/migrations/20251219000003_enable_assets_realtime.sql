-- Enable realtime for assets and workplace_assets tables
-- This allows clients to subscribe to postgres_changes for real-time updates
-- when assets are created, updated, or deleted

-- Add assets table for realtime updates on asset changes
ALTER PUBLICATION supabase_realtime ADD TABLE octupost.assets;

-- Add workplace_assets table for realtime updates when assets are linked to workspaces
ALTER PUBLICATION supabase_realtime ADD TABLE octupost.workplace_assets;

