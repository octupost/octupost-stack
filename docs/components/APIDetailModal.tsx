import { ApiRecord } from "@/lib/types";
import { formatUseCase } from "@/lib/useCases";
import { Badge } from "./Badge";
import { useEffect } from "react";

interface Props {
  api: ApiRecord | null;
  onClose: () => void;
}

function CodeBlock({ label, code }: { label: string; code?: string }) {
  if (!code) return null;
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-xs text-slate-400">
        <span>{label}</span>
        <button
          onClick={() => navigator.clipboard.writeText(code)}
          className="rounded-md border border-slate-700 px-2 py-1 text-[11px] text-slate-200 hover:border-accent"
        >
          Copy
        </button>
      </div>
      <pre className="whitespace-pre-wrap rounded-lg bg-slate-900/70 p-3 text-xs text-slate-100 border border-slate-800">
        {code}
      </pre>
    </div>
  );
}

export function APIDetailModal({ api, onClose }: Props) {
  useEffect(() => {
    if (!api) return;
    const onEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onEsc);
    return () => window.removeEventListener("keydown", onEsc);
  }, [api, onClose]);

  if (!api) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
      <div className="w-full max-w-4xl overflow-y-auto rounded-2xl border border-border bg-panel p-6 shadow-xl max-h-[90vh]">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="text-2xl font-semibold text-slate-100">{api.name}</div>
            <div className="text-sm uppercase tracking-wide text-slate-500">
              {api.subcategory}
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-full border border-slate-700 px-3 py-1 text-sm text-slate-300 hover:border-accent"
          >
            Close
          </button>
        </div>

        <p className="mt-3 text-slate-200">{api.description}</p>

        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          <InfoCard title="Pricing">
            <div className="text-slate-100 font-semibold">
              {api.pricePerUnit === 0
                ? "Free"
                : api.pricePerUnit !== undefined
                  ? `$${api.pricePerUnit} ${api.priceUnit ? ` / ${api.priceUnit}` : ""}`
                  : "See docs"}
            </div>
            <div className="text-xs text-slate-400 capitalize">{api.pricingModel}</div>
            {api.freeTier && (
              <div className="mt-1 text-xs text-emerald-300">
                Free tier: {api.freeTier.limit}
              </div>
            )}
          </InfoCard>

          <InfoCard title="Rate & Speed">
            <div className="text-slate-100 capitalize">{api.speed} speed</div>
            <div className="text-xs text-amber-300">{"★".repeat(api.quality)} quality</div>
          </InfoCard>

          <InfoCard title="Tech">
            <div className="flex flex-wrap gap-2">
              {api.sdks.map((sdk) => (
                <Badge key={sdk}>{sdk}</Badge>
              ))}
            </div>
            <div className="text-xs text-slate-400">Auth: {api.authType}</div>
          </InfoCard>
        </div>

        <div className="mt-4">
          <h4 className="text-sm font-semibold text-slate-100">Features</h4>
          <div className="mt-2 flex flex-wrap gap-2">
            {api.features.map((f) => (
              <Badge key={f}>{f}</Badge>
            ))}
          </div>
        </div>

        {api.useCases && api.useCases.length > 0 && (
          <div className="mt-4">
            <h4 className="text-sm font-semibold text-slate-100">Use cases</h4>
            <div className="mt-2 flex flex-wrap gap-2">
              {api.useCases.map((uc) => (
                <Badge key={uc}>{formatUseCase(uc)}</Badge>
              ))}
            </div>
          </div>
        )}

        <div className="mt-4 flex gap-3">
          <a
            href={api.website}
            target="_blank"
            rel="noreferrer"
            className="rounded-lg border border-border px-3 py-2 text-sm text-slate-100 hover:border-accent"
          >
            🔗 Website
          </a>
          <a
            href={api.docs}
            target="_blank"
            rel="noreferrer"
            className="rounded-lg border border-border px-3 py-2 text-sm text-slate-100 hover:border-accent"
          >
            📚 Docs
          </a>
        </div>

        <div className="mt-6 space-y-4">
          <h4 className="text-sm font-semibold text-slate-100">Code Examples</h4>
          <CodeBlock label="cURL" code={api.examples.curl} />
          <CodeBlock label="TypeScript" code={api.examples.typescript} />
          <CodeBlock label="Python" code={api.examples.python} />
        </div>
      </div>
    </div>
  );
}

function InfoCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-border bg-slate-900/40 p-3">
      <div className="text-xs uppercase tracking-wide text-slate-500">{title}</div>
      <div className="mt-2 space-y-1 text-sm">{children}</div>
    </div>
  );
}
