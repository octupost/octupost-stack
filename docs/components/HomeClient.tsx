/* eslint-disable react/no-unescaped-entities */
"use client";

import { useMemo, useState } from "react";
import { APICard } from "@/components/APICard";
import { APIDetailModal } from "@/components/APIDetailModal";
import { SearchBar } from "@/components/SearchBar";
import { filterAndSort, deriveCategories, Filters, SortOption, PricingFilter } from "@/lib/filtering";
import { ApiRecord, Category, UseCase } from "@/lib/types";
import { deriveUseCases, useCaseOptions } from "@/lib/useCases";

type Props = {
  apis: ApiRecord[];
};

export function HomeClient({ apis }: Props) {
  const enrichedApis = useMemo(
    () => apis.map((api) => ({ ...api, useCases: deriveUseCases(api) })),
    [apis]
  );
  const categories = useMemo(() => deriveCategories(enrichedApis), [enrichedApis]);
  const [query, setQuery] = useState("");
  const [filters, setFilters] = useState<Filters>({
    categories: new Set<Category>(),
    useCases: new Set<UseCase>(),
    pricing: "all"
  });
  const [sort, setSort] = useState<SortOption>("relevance");
  const [selected, setSelected] = useState<ApiRecord | null>(null);

  const { items } = useMemo(
    () => filterAndSort(enrichedApis, filters, query, sort),
    [enrichedApis, filters, query, sort]
  );

  const grouped = useMemo(() => {
    const bucket: Record<string, ApiRecord[]> = {};
    items.forEach((api) => {
      if (!bucket[api.category]) bucket[api.category] = [];
      bucket[api.category].push(api);
    });
    return bucket;
  }, [items]);

  const stats = [
    { label: "APIs", value: enrichedApis.length },
    { label: "Categories", value: categories.length },
    { label: "Docs & examples", value: enrichedApis.length * 3 }
  ];

  const pricingOptions: { value: PricingFilter; label: string }[] = [
    { value: "all", label: "Any pricing" },
    { value: "free", label: "Free" },
    { value: "has-free-tier", label: "Has free tier" },
    { value: "freemium", label: "Freemium" },
    { value: "paid", label: "Paid" }
  ];

  const toggleCategory = (cat: Category) => {
    setFilters((prev) => {
      const nextCategories = new Set(prev.categories);
      if (nextCategories.has(cat)) nextCategories.delete(cat);
      else nextCategories.add(cat);
      return { ...prev, categories: nextCategories };
    });
  };

  const toggleUseCase = (useCase: UseCase) => {
    setFilters((prev) => {
      const nextUseCases = new Set(prev.useCases);
      if (nextUseCases.has(useCase)) nextUseCases.delete(useCase);
      else nextUseCases.add(useCase);
      return { ...prev, useCases: nextUseCases };
    });
  };

  const reset = () => {
    setFilters({
      categories: new Set<Category>(),
      useCases: new Set<UseCase>(),
      pricing: "all"
    });
    setSort("relevance");
    setQuery("");
  };

  const handleStart = () => {
    const target = document.getElementById("api-explorer");
    if (target) {
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  return (
    <main className="mx-auto w-full max-w-none space-y-8 px-4 py-6 sm:px-6 lg:px-8">
      <Hero stats={stats} onStart={handleStart} />
      <ExplorerShell
        categories={categories}
        useCaseOptions={useCaseOptions}
        grouped={grouped}
        filters={filters}
        pricingOptions={pricingOptions}
        sort={sort}
        setSort={setSort}
        query={query}
        setQuery={setQuery}
        onToggleCategory={toggleCategory}
        onToggleUseCase={toggleUseCase}
        onPricingChange={(pricing) => setFilters((prev) => ({ ...prev, pricing }))}
        onSelect={setSelected}
        onReset={reset}
      />
      <APIDetailModal api={selected} onClose={() => setSelected(null)} />
    </main>
  );
}

function Hero({
  stats,
  onStart
}: {
  stats: { label: string; value: number }[];
  onStart: () => void;
}) {
  return (
    <section className="rounded-3xl border border-border bg-slate-950/70 p-6 shadow-lg">
      <div className="flex flex-col gap-4">
        <div className="inline-flex w-fit items-center gap-2 rounded-full border border-slate-800 bg-slate-900/70 px-3 py-1 text-xs uppercase tracking-wide text-slate-400">
          Research • Media agent
        </div>
        <h1 className="text-3xl font-semibold text-slate-50">Media generation APIs in one simple view</h1>
        <p className="max-w-3xl text-sm text-slate-300">
          Inspired by fal.ai's minimal docs experience: quick search, lightweight filters, and per-category anchors so you
          can jump to what matters without a heavy sidebar.
        </p>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={onStart}
            className="rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-slate-900 shadow-sm transition hover:brightness-110"
          >
            Start exploring
          </button>
        </div>
        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          {stats.map((stat) => (
            <div key={stat.label} className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 shadow-inner">
              <div className="text-xs uppercase tracking-wide text-slate-500">{stat.label}</div>
              <div className="text-2xl font-semibold text-slate-50">{stat.value}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

type ExplorerShellProps = {
  categories: Category[];
  useCaseOptions: { value: UseCase; label: string }[];
  grouped: Record<string, ApiRecord[]>;
  filters: Filters;
  pricingOptions: { value: PricingFilter; label: string }[];
  sort: SortOption;
  setSort: (sort: SortOption) => void;
  query: string;
  setQuery: (value: string) => void;
  onToggleCategory: (cat: Category) => void;
  onToggleUseCase: (useCase: UseCase) => void;
  onPricingChange: (pricing: PricingFilter) => void;
  onSelect: (api: ApiRecord) => void;
  onReset: () => void;
};

function ExplorerShell({
  categories,
  useCaseOptions,
  grouped,
  filters,
  pricingOptions,
  sort,
  setSort,
  query,
  setQuery,
  onToggleCategory,
  onToggleUseCase,
  onPricingChange,
  onSelect,
  onReset
}: ExplorerShellProps) {
  const total = Object.values(grouped).reduce((acc, list) => acc + list.length, 0);
  const activeCategories = filters.categories.size;
  const activeUseCases = filters.useCases.size;

  const scrollToSection = (cat: Category) => {
    const el = document.getElementById(`section-${cat}`);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <section id="api-explorer" className="space-y-6">
      <div className="space-y-3 rounded-2xl border border-border bg-panel p-4 shadow-sm">
        <div className="flex flex-wrap items-center gap-3">
          <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-200">
            {total} APIs
          </span>
          <span className="text-xs text-slate-500">
            Search, pick categories, skim by anchor links. Lightweight and fast.
          </span>
        </div>
        <div className="flex flex-wrap gap-3">
          <SearchBar
            value={query}
            onChange={setQuery}
            placeholder="Search by name, feature, or category..."
            className="w-full min-w-[240px] sm:w-72"
          />
          <select
            className="rounded-lg border border-border bg-slate-900 px-3 py-2 text-sm text-slate-200 focus:border-accent"
            value={filters.pricing}
            onChange={(e) => onPricingChange(e.target.value as PricingFilter)}
          >
            {pricingOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>
                Pricing: {opt.label}
              </option>
            ))}
          </select>
          <select
            className="rounded-lg border border-border bg-slate-900 px-3 py-2 text-sm text-slate-200 focus:border-accent"
            value={sort}
            onChange={(e) => setSort(e.target.value as SortOption)}
          >
            <option value="relevance">Sort: relevance</option>
            <option value="quality">Sort: quality</option>
            <option value="name">Sort: name</option>
          </select>
          <button
            className="text-xs text-accent underline-offset-2 hover:underline"
            onClick={onReset}
          >
            Reset
          </button>
        </div>

        <div className="space-y-2">
          <div className="text-xs uppercase tracking-wide text-slate-500">Categories</div>
          <div className="flex flex-wrap gap-2">
            {categories.map((cat) => {
              const active = filters.categories.has(cat);
              return (
                <button
                  key={cat}
                  onClick={() => onToggleCategory(cat)}
                  className={`rounded-full border px-3 py-1 text-xs font-medium transition ${
                    active
                      ? "border-accent bg-accent text-slate-900"
                      : "border-slate-700 bg-slate-900/70 text-slate-200 hover:border-accent"
                  }`}
                >
                  {formatCategory(cat)}
                </button>
              );
            })}
          </div>
          <div className="flex flex-wrap gap-2 text-xs text-slate-400">
            <span className="text-slate-500">Jump to:</span>
            {categories.map((cat) => (
              <button
                key={`anchor-${cat}`}
                className="underline underline-offset-2 hover:text-slate-100"
                onClick={() => scrollToSection(cat)}
              >
                {formatCategory(cat)}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-2">
          <div className="text-xs uppercase tracking-wide text-slate-500">Use cases</div>
          <div className="flex flex-wrap gap-2">
            {useCaseOptions.map((useCase) => {
              const active = filters.useCases.has(useCase.value);
              return (
                <button
                  key={useCase.value}
                  onClick={() => onToggleUseCase(useCase.value)}
                  className={`rounded-full border px-3 py-1 text-xs font-medium transition ${
                    active
                      ? "border-accent bg-accent text-slate-900"
                      : "border-slate-700 bg-slate-900/70 text-slate-200 hover:border-accent"
                  }`}
                >
                  {useCase.label}
                </button>
              );
            })}
          </div>
        </div>

        {(activeCategories > 0 || activeUseCases > 0) && (
          <div className="text-[11px] text-slate-500">
            {activeCategories > 0
              ? `${activeCategories} categor${activeCategories === 1 ? "y" : "ies"}`
              : null}
            {activeCategories > 0 && activeUseCases > 0 ? " • " : ""}
            {activeUseCases > 0
              ? `${activeUseCases} use case${activeUseCases === 1 ? "" : "s"}`
              : null}{" "}
            selected
          </div>
        )}
      </div>

      <div className="space-y-8">
        {total === 0 ? (
          <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-900/60 p-6 text-sm text-slate-300">
            No APIs match that filter. Try clearing a category or switching pricing.
          </div>
        ) : (
          categories.map((cat) => {
            const list = grouped[cat] ?? [];
            if (!list.length) return null;
            return (
              <section key={cat} id={`section-${cat}`} className="space-y-3 scroll-mt-20">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-xs uppercase tracking-wide text-slate-500">Category</div>
                    <h3 className="text-xl font-semibold text-slate-100">
                      {formatCategory(cat)} <span className="text-sm text-slate-500">({list.length})</span>
                    </h3>
                  </div>
                  <button
                    className="text-xs text-accent underline-offset-2 hover:underline"
                    onClick={() => scrollToSection(cat)}
                  >
                    Back to top
                  </button>
                </div>
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {list.map((api) => (
                    <APICard key={api.id} api={api} onSelect={onSelect} />
                  ))}
                </div>
              </section>
            );
          })
        )}
      </div>
    </section>
  );
}

function formatCategory(cat: Category) {
  return cat.replace(/-/g, " ");
}
