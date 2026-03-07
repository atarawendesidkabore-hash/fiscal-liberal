"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";

type Message = {
  role: "user" | "assistant";
  text: string;
};

export default function AIChat() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      text: "Bonjour, je suis votre assistant fiscal. Posez une question sur le CGI, la liasse 2058-A ou le calcul IS."
    }
  ]);

  const submit = async () => {
    if (!question.trim() || loading) return;
    const userMessage: Message = { role: "user", text: question.trim() };
    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");
    setLoading(true);
    try {
      const result = await api.searchCgi(userMessage.text);
      const first = result.results?.[0];
      const answer = first
        ? `Reference: ${first.article}\n${first.title}\n${first.excerpt}`
        : "Aucune reference directe trouvee. Reformulez votre question.";
      setMessages((prev) => [...prev, { role: "assistant", text: answer }]);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Erreur IA";
      setMessages((prev) => [...prev, { role: "assistant", text: `Erreur: ${message}` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Assistant Fiscal IA</CardTitle>
        <CardDescription>Question libre sur CGI, 2058-A, regimes fiscaux et alertes.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="max-h-[420px] space-y-3 overflow-y-auto rounded-md border p-3">
          {messages.map((message, index) => (
            <div
              key={`${message.role}-${index}`}
              className={
                message.role === "assistant"
                  ? "rounded-md bg-muted p-3 text-sm"
                  : "ml-auto max-w-[85%] rounded-md bg-primary p-3 text-sm text-primary-foreground"
              }
            >
              <p className="whitespace-pre-wrap">{message.text}</p>
            </div>
          ))}
        </div>

        <div className="flex gap-2">
          <Input
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ex: Traitement de la ligne WI dans la 2058-A"
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                event.preventDefault();
                void submit();
              }
            }}
          />
          <Button type="button" onClick={() => void submit()} disabled={loading}>
            {loading ? "Analyse..." : "Envoyer"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

