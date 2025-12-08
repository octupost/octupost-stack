import { ApiRecord } from "@/lib/types";
import { formatUseCase } from "@/lib/useCases";
import { Badge } from "./Badge";

interface Props {
  api: ApiRecord;
  onSelect: (api: ApiRecord) => void;
}

const categoryIcons: Record<string, string> = {
  visuals: "🎨",
  video: "🎬",
  audio: "🔊",
  "data-sources": "📦",
  translation: "🌐",
  utils: "🔧"
};

export function APICard({ api, onSelect }: Props) {
  return (
    <div className="card flex flex-col gap-3">
      <div className="flex items-start justify-between gap-2">
        <div>
          <div className="text-lg font-semibold text-slate-100 flex items-center gap-2">
            <span>{categoryIcons[api.category] ?? "•"}</span>
            {api.name}
          </div>
          <div className="text-xs uppercase tracking-wide text-slate-500">
            {api.subcategory}
          </div>
        </div>
        <div className="flex gap-1">
          <Badge>{api.pricingTier}</Badge>
          <Badge>{api.pricingModel.replace(/-/g, " ")}</Badge>
        </div>
      </div>

      <p className="text-sm text-slate-300 line-clamp-3">{api.description}</p>

      {api.useCases && api.useCases.length > 0 && (
        <div className="flex flex-wrap gap-2 text-[11px] text-slate-300">
          {api.useCases.slice(0, 3).map((u) => (
            <Badge key={u}>{formatUseCase(u)}</Badge>
          ))}
        </div>
      )}

      <div className="flex flex-wrap gap-2 text-xs text-slate-300">
        {api.features.slice(0, 4).map((f) => (
          <Badge key={f}>{f}</Badge>
        ))}
      </div>

      <div className="flex items-center justify-between text-sm text-slate-200">
        <div className="flex items-center gap-2">
          <span className="text-amber-300">{"★".repeat(api.quality)}</span>
          <span className="text-slate-500">Quality</span>
        </div>
        <div className="text-slate-200 font-semibold">
          {api.pricePerUnit === 0
            ? "Free"
            : Number.isFinite(api.pricePerUnit)
              ? `$${Number(api.pricePerUnit).toFixed(3)}`
              : "—"}
          {api.priceUnit ? <span className="text-xs text-slate-500"> / {api.priceUnit}</span> : null}
        </div>
      </div>

      <button
        onClick={() => onSelect(api)}
        className="mt-auto w-full rounded-lg bg-accent px-3 py-2 text-sm font-semibold text-slate-900 transition hover:brightness-110"
      >
        View details
      </button>
    </div>
  );
}
