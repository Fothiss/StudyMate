import { Clock3 } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

type UnavailableSectionProps = {
  title: string;
  description: string;
  className?: string;
};

/**
 * Раздел, которого ещё нет. Намеренно без кнопок и ссылок: интерфейс
 * объясняет причину, а не предлагает действие, которое не сработает.
 */
export function UnavailableSection({ title, description, className }: UnavailableSectionProps) {
  return (
    <Card className={cn("border-dashed bg-muted/30 shadow-none", className)}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 font-heading text-base text-muted-foreground">
          <Clock3 className="size-4" aria-hidden />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  );
}
