interface Props {
  value: number;
  min?: number;
  max?: number;
  step?: number;
  onChange: (value: number) => void;
}

export function PriceSlider({
  value,
  min = 0,
  max = 1,
  step = 0.01,
  onChange
}: Props) {
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs text-slate-400">
        <span>Max price</span>
        <span className="font-semibold text-slate-200">${value.toFixed(2)}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full accent-accent"
      />
      <div className="flex justify-between text-[11px] text-slate-500">
        <span>${min}</span>
        <span>${max}</span>
      </div>
    </div>
  );
}

