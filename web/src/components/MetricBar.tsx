interface Props {
  label: string;
  value: number;
  weight: string;
  delay?: number;
}

function barColor(v: number) {
  if (v >= 8) return "bg-[#a3fb73]";
  if (v >= 7) return "bg-[#7dd151]";
  if (v >= 5) return "bg-[#f59e0b]";
  return "bg-red-500";
}

function textColor(v: number) {
  if (v >= 8) return "text-[#a3fb73]";
  if (v >= 7) return "text-[#7dd151]";
  if (v >= 5) return "text-[#f59e0b]";
  return "text-red-400";
}

export function MetricBar({ label, value, weight, delay = 0 }: Props) {
  const pct = Math.min(100, (value / 10) * 100);

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-sm font-mono text-[#7a9b87]">{label}</span>
          <span className="text-[10px] font-mono text-[#3d5a44]">{weight}</span>
        </div>
        <span className={`text-sm font-mono font-bold tabular-nums ${textColor(value)}`}>
          {value.toFixed(1)}
        </span>
      </div>
      <div className="h-1.5 bg-[#243d2c] rounded-full overflow-hidden border border-[#a3fb73]/8">
        <div
          className={`h-full rounded-full transition-all duration-700 ease-out ${barColor(value)}`}
          style={{ width: `${pct}%`, transitionDelay: `${delay}ms` }}
        />
      </div>
    </div>
  );
}
