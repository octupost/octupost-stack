import Fuse from "fuse.js";
import { ApiRecord, Category, UseCase } from "./types";

export type PricingFilter = "all" | "free" | "freemium" | "paid" | "has-free-tier";
export type SortOption = "relevance" | "quality" | "name";

export interface Filters {
  categories: Set<Category>;
  useCases: Set<UseCase>;
  pricing: PricingFilter;
}

export interface SearchResult {
  items: ApiRecord[];
  fuse?: Fuse<ApiRecord>;
}

export function createFuse(data: ApiRecord[]) {
  return new Fuse(data, {
    keys: [
      "name",
      "description",
      "subcategory",
      "features",
      "pricingModel",
      "pricingTier"
    ],
    threshold: 0.33,
    ignoreLocation: true
  });
}

function passesFilters(api: ApiRecord, filters: Filters) {
  if (filters.categories.size && !filters.categories.has(api.category)) return false;

  if (filters.useCases.size) {
    const matchesUseCase = (api.useCases ?? []).some((u) => filters.useCases.has(u));
    if (!matchesUseCase) return false;
  }

  if (filters.pricing !== "all") {
    if (filters.pricing === "has-free-tier") {
      if (!api.freeTier || api.pricingTier === "paid") return false;
    } else if (api.pricingTier !== filters.pricing) {
      return false;
    }
  }

  return true;
}

export function filterAndSort(
  data: ApiRecord[],
  filters: Filters,
  query: string,
  sort: SortOption
) {
  const fuse = createFuse(data);
  let candidates = data;

  if (query.trim()) {
    candidates = fuse.search(query.trim()).map((r) => r.item);
  }

  const filtered = candidates.filter((api) => passesFilters(api, filters));

  const sorted = [...filtered].sort((a, b) => {
    switch (sort) {
      case "quality":
        return b.quality - a.quality;
      case "name":
        return a.name.localeCompare(b.name);
      default:
        return 0;
    }
  });

  return { items: sorted, fuse };
}

export function collectUnique<T>(values: T[]): T[] {
  return Array.from(new Set(values));
}

export function deriveCategories(data: ApiRecord[]) {
  return collectUnique(data.map((d) => d.category));
}
