import { Sparkles } from "lucide-react";
import { Link } from "react-router";

import { cn } from "@/lib/utils";

type BrandProps = {
  compact?: boolean;
  className?: string;
};

export function Brand({ compact = false, className }: BrandProps) {
  return (
    <Link
      to="/"
      className={cn("flex items-center gap-2.5 rounded-xl outline-none", className)}
      aria-label="StudyMate"
    >
      <span className="sheen grid size-9 place-items-center rounded-xl bg-gradient-to-br from-[var(--aurora-1)] via-[var(--aurora-2)] to-[var(--aurora-3)] text-white shadow-lg shadow-[var(--aurora-1)]/25">
        <Sparkles className="size-4" aria-hidden />
      </span>
      {!compact && (
        <span className="font-heading text-base font-extrabold tracking-tight">StudyMate</span>
      )}
    </Link>
  );
}
