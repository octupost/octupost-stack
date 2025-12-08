import { Filters, PricingFilter } from "@/lib/filtering";
import { Category, UseCase } from "@/lib/types";
import { useCaseOptions } from "@/lib/useCases";

interface Props {
  filters: Filters;
  categories: Category[];
  onFiltersChange: (filters: Filters) => void;
}

function toggleSet<T>(set: Set<T>, value: T) {
  const next = new Set(set);
  if (next.has(value)) next.delete(value);
  else next.add(value);
  return next;
}

export function FilterSidebar({ filters, categories, onFiltersChange }: Props) {
  const update = (next: Partial<Filters>) => {
    onFiltersChange({ ...filters, ...next });
  };

  const pricingOptions: { value: PricingFilter; label: string }[] = [
    { value: "all", label: "All" },
    { value: "free", label: "Free only" },
    { value: "has-free-tier", label: "Has free tier" },
    { value: "freemium", label: "Freemium" },
    { value: "paid", label: "Paid" }
  ];

  return (
    <aside className="w-full max-w-xs space-y-6 rounded-xl border border-border bg-panel p-4">
      <div>
        <h3 className="text-sm font-semibold text-slate-100">Category</h3>
        <div className="mt-2 space-y-1">
          {categories.map((cat) => (
            <label key={cat} className="flex items-center gap-2 text-sm text-slate-300">
              <input
                type="checkbox"
                className="accent-accent"
                checked={filters.categories.has(cat)}
                onChange={() =>
                  update({ categories: toggleSet(filters.categories, cat) })
                }
              />
              <span className="capitalize">{cat.replace("-", " ")}</span>
            </label>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-sm font-semibold text-slate-100">Pricing</h3>
        <div className="mt-2 space-y-1">
          {pricingOptions.map((opt) => (
            <label key={opt.value} className="flex items-center gap-2 text-sm text-slate-300">
              <input
                type="radio"
                name="pricing"
                className="accent-accent"
                checked={filters.pricing === opt.value}
                onChange={() => update({ pricing: opt.value })}
              />
              <span>{opt.label}</span>
            </label>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-sm font-semibold text-slate-100">Use cases</h3>
        <div className="mt-2 space-y-1">
          {useCaseOptions.map((opt) => (
            <label key={opt.value} className="flex items-center gap-2 text-sm text-slate-300">
              <input
                type="checkbox"
                className="accent-accent"
                checked={filters.useCases.has(opt.value)}
                onChange={() =>
                  update({ useCases: toggleSet(filters.useCases, opt.value) })
                }
              />
              <span>{opt.label}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="pt-2">
        <button
          className="text-xs text-accent underline-offset-2 hover:underline"
          onClick={() =>
            update({
              categories: new Set<Category>(),
              useCases: new Set<UseCase>(),
              pricing: "all"
            })
          }
        >
          Reset
        </button>
      </div>
    </aside>
  );
}
