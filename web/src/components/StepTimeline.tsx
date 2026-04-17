"use client";

import { useState } from "react";
import { CheckCircle2, XCircle, MinusCircle, Camera, ChevronDown, ChevronUp } from "lucide-react";
import type { BistStep } from "@/types";

function stepIcon(status: string) {
  if (status === "passed")  return <CheckCircle2 className="w-3.5 h-3.5 text-[#a3fb73] shrink-0 mt-0.5" />;
  if (status === "failed")  return <XCircle      className="w-3.5 h-3.5 text-red-400   shrink-0 mt-0.5" />;
  return                           <MinusCircle  className="w-3.5 h-3.5 text-[#5a7a65] shrink-0 mt-0.5" />;
}

function fmtMs(ms: number) {
  if (!ms) return "";
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}

function keywordColor(kw: string) {
  const k = kw.toLowerCase();
  if (k === "dado" || k === "given")  return "text-[#60a5fa]";
  if (k === "quando" || k === "when") return "text-[#f59e0b]";
  if (k === "então" || k === "then")  return "text-[#a3fb73]";
  return "text-[#7a9b87]";
}

function parseStep(text: string): { keyword: string; body: string } {
  const m = text.match(/^(Dado|Quando|Então|Given|When|Then|And|E|Mas|But)\s+(.*)/i);
  if (m) return { keyword: m[1], body: m[2] };
  return { keyword: "", body: text };
}

export function StepTimeline({ steps }: { steps: BistStep[] }) {
  const [openScreenshot, setOpenScreenshot] = useState<string | null>(null);

  if (!steps.length) return (
    <p className="text-xs font-mono text-[#3d5a44] py-2">sem steps registrados</p>
  );

  return (
    <>
      <div className="space-y-1">
        {steps.map((step, i) => {
          const { keyword, body } = parseStep(step.step_text);
          const isLast = i === steps.length - 1;

          return (
            <div key={step.id} className="flex gap-2.5">
              {/* Timeline connector */}
              <div className="flex flex-col items-center">
                {stepIcon(step.status)}
                {!isLast && <div className="w-px flex-1 bg-[#a3fb73]/8 mt-1" />}
              </div>

              {/* Step content */}
              <div className="pb-2 min-w-0 flex-1">
                <div className="flex items-start justify-between gap-2">
                  <p className="text-xs font-mono text-[#c8e8c8] leading-relaxed">
                    {keyword && (
                      <span className={`${keywordColor(keyword)} mr-1.5`}>{keyword}</span>
                    )}
                    {body}
                  </p>
                  <div className="flex items-center gap-1.5 shrink-0">
                    {step.duration_ms > 0 && (
                      <span className="text-[9px] font-mono text-[#3d5a44] tabular-nums">
                        {fmtMs(step.duration_ms)}
                      </span>
                    )}
                    {step.screenshot_path && (
                      <button
                        onClick={() => setOpenScreenshot(
                          openScreenshot === step.screenshot_path ? null : step.screenshot_path
                        )}
                        className="text-[#5a7a65] hover:text-[#a3fb73] transition-colors"
                        title="ver screenshot"
                      >
                        <Camera className="w-3 h-3" />
                      </button>
                    )}
                  </div>
                </div>

                {/* Screenshot preview */}
                {openScreenshot === step.screenshot_path && step.screenshot_path && (
                  <div className="mt-2 rounded overflow-hidden border border-[#a3fb73]/15 max-w-sm">
                    <img
                      src={step.screenshot_path}
                      alt={`screenshot step ${step.id}`}
                      className="w-full h-auto"
                    />
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Full-screen screenshot modal */}
      {openScreenshot && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-6"
          style={{ background: "rgba(10,20,13,0.92)", backdropFilter: "blur(8px)" }}
          onClick={() => setOpenScreenshot(null)}
        >
          <img
            src={openScreenshot}
            alt="screenshot"
            className="max-w-full max-h-full rounded shadow-2xl border border-[#a3fb73]/20"
            onClick={e => e.stopPropagation()}
          />
        </div>
      )}
    </>
  );
}
