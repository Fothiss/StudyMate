import Link from "next/link";

import { Button } from "@/components/ui/button";

type HeaderProps = {
  login: string | null;
  onSignOut: () => void;
};

export function Header({ login, onSignOut }: HeaderProps) {
  return (
    <header className="border-b">
      <div className="mx-auto flex w-full max-w-5xl items-center justify-between gap-4 px-6 py-3">
        <Link href="/" className="text-base font-semibold">
          StudyMate
        </Link>
        <div className="flex items-center gap-3">
          <span className="text-sm text-muted-foreground">{login ?? "…"}</span>
          <Button variant="outline" size="sm" onClick={onSignOut}>
            Выйти
          </Button>
        </div>
      </div>
    </header>
  );
}
