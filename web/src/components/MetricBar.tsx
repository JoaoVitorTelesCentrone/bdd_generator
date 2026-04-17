interface Props {
  label: string;
  value: number;
  weight: string;
  delay?: number;
}

function barColor(v: number) {
  if (v >= 8) return "bg-[#a3fb73]";
  if (v >= 7) return "bg-[#7dd151]";
  if (v >= 5) return "bg-amber-400";
  return "bg-red-400";
}

function textColor(v: number) {
  if (v >= 8) return "text-[#2D6A3F]";
  if (v >= 7) return "text-[#3d7a4a]";
  if (v >= 5) return "text-amber-600";
  return "text-red-500";
}

export function MetricBar({ label, value, weight, delay = 0 }: Props) {
  const pct = Math.min(100, (value / 10) * 100);

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-sm text-bist-mid">{label}</span>
          <span className="text-[10px] font-code text-bist-dim bg-bist-surface2 border border-bist-border2 rounded px-1.5 py-0.5">{weight}</span>
        </div>
        <span className={`text-sm font-code font-semibold tabular-nums ${textColor(value)}`}>
          {value.toFixed(1)}
        </span>
      </div>
      <div className="h-1.5 bg-bist-border rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ease-out ${barColor(value)}`}
          style={{ width: `${pct}%`, transitionDelay: `${delay}ms` }}
        />
      </div>
    </div>
  );
}
