interface Props {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
}

export function SearchBar({ value, onChange, placeholder, className }: Props) {
  return (
    <input
      className={`w-full rounded-lg border border-border bg-panel px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-accent focus:outline-none ${className ?? ""}`}
      placeholder={placeholder ?? "Search..."}
      value={value}
      onChange={(e) => onChange(e.target.value)}
    />
  );
}

