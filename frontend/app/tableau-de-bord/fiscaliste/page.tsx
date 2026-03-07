import AIChat from "@/components/ai/AIChat";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function FiscalistePage() {
  return (
    <section className="space-y-5">
      <Card>
        <CardHeader>
          <CardTitle>Espace Fiscaliste IA</CardTitle>
          <CardDescription>Posez vos questions fiscales libres et obtenez des references rapides.</CardDescription>
        </CardHeader>
      </Card>
      <AIChat />
    </section>
  );
}

