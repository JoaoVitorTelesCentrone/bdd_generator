"use client";

import { useState } from "react";
import { CheckCircle2, XCircle, MinusCircle, Camera } from "lucide-react";
import type { BistStep } from "@/types";

function stepIcon(status: string) {
  if (status === "passed")  return <CheckCircle2 className="w-3.5 h-3.5 text-[#2D6A3F] shrink-0 mt-0.5" />;
  if (status === "failed")  return <XCircle      className="w-3.5 h-3.5 text-red-500   shrink-0 mt-0.5" />;
  return                           <MinusCircle  className="w-3.5 h-3.5 text-bist-muted shrink-0 mt-0.5" />;
}

function fmtMs(ms: number) {
  if (!ms) return "";
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}

function keywordColor(kw: string) {
  const k = kw.toLowerCase();
  if (k === "dado" || k === "given")   return "text-blue-500";
  if (k === "quando" || k === "when")  return "text-amber-600";
  if (k === "então" || k === "then")   return "text-[#2D6A3F]";
  return "text-bist-muted";
}

function parseStep(text: string): { keyword: string; body: string } {
  const m = text.match(/^(Dado|Quando|Então|Given|When|Then|And|E|Mas|But)\s+(.*)/i);
  if (m) return { keyword: m[1], body: m[2] };
  return { keyword: "", body: text };
}

export function StepTimeline({ steps }: { steps: BistStep[] }) {
  const [openScreenshot, setOpenScreenshot] = useState<string | null>(null);

  if (!steps.length) return (
    <p className="text-xs text-bist-muted py-2">Sem steps registrados</p>
  );

  return (
    <>
      <div className="space-y-1">
        {steps.map((step, i) => {
          const { keyword, body } = parseStep(step.step_text);
          const isLast = i === steps.length - 1;

          return (
            <div key={step.id} className="flex gap-2.5">
              <div className="flex flex-col items-center">
                {stepIcon(step.status)}
                {!isLast && <div className="w-px flex-1 bg-bist-border mt-1" />}
              </div>
              <div className="pb-2 min-w-0 flex-1">
                <div className="flex items-start justify-between gap-2">
                  <p className="text-xs font-code text-bist-mid leading-relaxed">
                    {keyword && <span className={`${keywordColor(keyword)} mr-1.5 font-semibold`}>{keyword}</span>}
                    {body}
                  </p>
                  <div className="flex items-center gap-1.5 shrink-0">
                    {step.duration_ms > 0 && (
                      <span className="text-[9px] font-code text-bist-dim tabular-nums">{fmtMs(step.duration_ms)}</span>
                    )}
                    {step.screenshot_path && (
                      <button
                        onClick={() => setOpenScreenshot(openScreenshot === step.screenshot_path ? null : step.screenshot_path)}
                        className="text-bist-muted hover:text-bist-primary transition-colors"
                      >
                        <Camera className="w-3 h-3" />
                      </button>
                    )}
                  </div>
                </div>
                {openScreenshot === step.screenshot_path && step.screenshot_path && (
                  <div className="mt-2 rounded-lg overflow-hidden border border-bist-border max-w-sm">
                    <img src={step.screenshot_path} alt={`screenshot step ${step.id}`} className="w-full h-auto" />
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {openScreenshot && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/60 backdrop-blur-sm"
          onClick={() => setOpenScreenshot(null)}
        >
          <img
            src={openScreenshot}
            alt="screenshot"
            className="max-w-full max-h-full rounded-xl shadow-2xl border border-white/20"
            onClick={e => e.stopPropagation()}
          />
        </div>
      )}
    </>
  );
}
