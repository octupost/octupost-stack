-- Create workplace_assets join table to associate assets with workplaces
-- Depends on octupost.workplaces and octupost.assets

begin;

create table if not exists octupost.workplace_assets (
  id uuid primary key default gen_random_uuid(),
  workplace_id uuid not null references octupost.workplaces(id) on delete cascade,
  asset_id uuid not null references octupost.assets(id) on delete cascade,
  created_at_utc timestamptz not null default now(),
  constraint workplace_assets_workplace_asset_unique unique (workplace_id, asset_id)
);

create index if not exists idx_workplace_assets_asset_id on octupost.workplace_assets(asset_id);
create index if not exists idx_workplace_assets_workplace_id on octupost.workplace_assets(workplace_id);

commit;

