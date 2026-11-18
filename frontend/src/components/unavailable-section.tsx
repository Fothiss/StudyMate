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
    <Card className={cn("bg-muted/40", className)}>
      <CardHeader>
        <CardTitle className="text-muted-foreground">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  );
}
