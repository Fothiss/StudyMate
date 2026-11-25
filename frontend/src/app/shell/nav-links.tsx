import { BookOpenCheck, ChartNoAxesColumn, LayoutDashboard } from "lucide-react";
import { NavLink } from "react-router";

import { cn } from "@/lib/utils";

const ITEMS = [
  { to: "/", label: "Обзор", icon: LayoutDashboard, end: true },
  { to: "/quiz", label: "Тест", icon: BookOpenCheck, end: false },
  { to: "/results", label: "Результаты", icon: ChartNoAxesColumn, end: false },
];

type NavLinksProps = {
  orientation?: "vertical" | "horizontal";
};

export function NavLinks({ orientation = "vertical" }: NavLinksProps) {
  const vertical = orientation === "vertical";

  return (
    <nav className={cn("flex gap-1", vertical ? "flex-col" : "flex-row")}>
      {ITEMS.map(({ to, label, icon: Icon, end }) => (
        <NavLink
          key={to}
          to={to}
          end={end}
          className={({ isActive }) =>
            cn(
              "flex items-center gap-3 rounded-xl text-sm font-medium transition-colors",
              vertical ? "px-3 py-2" : "px-2.5 py-1.5",
              isActive
                ? "bg-primary/15 text-foreground ring-1 ring-primary/30"
                : "text-muted-foreground hover:bg-secondary hover:text-foreground",
            )
          }
        >
          {({ isActive }) => (
            <>
              <Icon
                className={cn("size-4", isActive ? "text-primary" : "text-muted-foreground")}
                aria-hidden
              />
              <span className={cn(!vertical && "sr-only sm:not-sr-only")}>{label}</span>
            </>
          )}
        </NavLink>
      ))}
    </nav>
  );
}
