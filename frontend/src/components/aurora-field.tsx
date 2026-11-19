/**
 * Декоративный фон: три радиальных пятна, два плывущих «облака» и зерно.
 * Полностью `aria-hidden` и без перехвата событий; при
 * `prefers-reduced-motion: reduce` анимация отключается в CSS.
 */
export function AuroraField() {
  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden" aria-hidden>
      <div className="aurora-field" />
      <div
        className="aurora-orb top-[8%] -left-24 size-[28rem] bg-[var(--aurora-1)]"
        style={{ animationDelay: "-4s" }}
      />
      <div
        className="aurora-orb top-[42%] -right-20 size-[22rem] bg-[var(--aurora-2)]"
        style={{ animationDelay: "-12s" }}
      />
      <div className="aurora-grain" />
    </div>
  );
}
