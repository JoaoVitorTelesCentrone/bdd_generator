interface Props {
  label: string;
  value: number;
  weight: string;
  delay?: number;
}

function scoreColor(v: number) {
  if (v >= 8)  return "bg-emerald-500";
  if (v >= 7)  return "bg-green-500";
  if (v >= 5)  return "bg-amber-500";
  return "bg-red-500";
}

function scoreTextColor(v: number) {
  if (v >= 8)  return "text-emerald-400";
  if (v >= 7)  return "text-green-400";
  if (v >= 5)  return "text-amber-400";
  return "text-red-400";
}

export function MetricBar({ label, value, weight, delay = 0 }: Props) {
  const pct = Math.min(100, (value / 10) * 100);

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-sm text-zinc-300 font-medium">{label}</span>
          <span className="text-xs text-zinc-600">{weight}</span>
        </div>
        <span className={`text-sm font-semibold tabular-nums ${scoreTextColor(value)}`}>
          {value.toFixed(1)}
        </span>
      </div>
      <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ease-out ${scoreColor(value)}`}
          style={{
            width: `${pct}%`,
            transitionDelay: `${delay}ms`,
          }}
        />
      </div>
    </div>
  );
}
