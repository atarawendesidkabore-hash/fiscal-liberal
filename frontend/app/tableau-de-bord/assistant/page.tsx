import AIChat from "@/components/ai/AIChat";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function AssistantPage() {
  return (
    <section className="space-y-5">
      <Card>
        <CardHeader>
          <CardTitle>Assistant fiscal IA</CardTitle>
          <CardDescription>Posez vos questions libres sur le CGI, IS, liasse 2058-A et regimes speciaux.</CardDescription>
        </CardHeader>
      </Card>
      <AIChat />
    </section>
  );
}

