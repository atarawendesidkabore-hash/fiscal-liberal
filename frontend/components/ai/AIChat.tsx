"use client";

import { RotateCcw, Send } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useToast } from "@/lib/toast";
import { api } from "@/lib/api";

type Message = {
  id: string;
  role: "user" | "assistant";
  text: string;
  createdAt: string;
};

const STORAGE_KEY = "fiscia-ai-history-v1";

function createId(prefix: string) {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
}

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export default function AIChat() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [mounted, setMounted] = useState(false);
  const { push } = useToast();

  useEffect(() => {
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw) as Message[];
        if (Array.isArray(parsed) && parsed.length > 0) {
          setMessages(parsed);
          setMounted(true);
          return;
        }
      }
    } catch {
      push({ title: "Historique invalide", description: "Impossible de charger l'historique local.", variant: "error" });
    }

    setMessages([
      {
        id: createId("assistant"),
        role: "assistant",
        text: "Bonjour, je suis votre assistant fiscal. Posez une question sur le CGI, la liasse 2058-A ou le calcul IS.",
        createdAt: new Date().toISOString()
      }
    ]);
    setMounted(true);
  }, [push]);

  useEffect(() => {
    if (!mounted) return;
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
  }, [messages, mounted]);

  const canSend = useMemo(() => question.trim().length > 0 && !loading, [question, loading]);

  const streamAssistantAnswer = async (id: string, text: string) => {
    setMessages((prev) => [...prev, { id, role: "assistant", text: "", createdAt: new Date().toISOString() }]);

    const step = Math.max(3, Math.round(text.length / 60));
    for (let index = step; index <= text.length + step; index += step) {
      const next = text.slice(0, Math.min(index, text.length));
      setMessages((prev) => prev.map((msg) => (msg.id === id ? { ...msg, text: next } : msg)));
      await sleep(18);
    }
  };

  const submit = async () => {
    if (!canSend) return;

    const value = question.trim();
    const userMessage: Message = {
      id: createId("user"),
      role: "user",
      text: value,
      createdAt: new Date().toISOString()
    };

    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");
    setLoading(true);

    try {
      const result = await api.searchCgi(value);
      const first = result.results?.[0];
      const answer = first
        ? `Reference: ${first.article}\n${first.title}\n\n${first.excerpt}`
        : "Aucune reference directe trouvee. Reformulez votre question en precisant l'article ou le regime fiscal.";
      await streamAssistantAnswer(createId("assistant"), answer);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Erreur IA";
      await streamAssistantAnswer(createId("assistant"), `Erreur: ${message}`);
      push({ title: "Requete IA en echec", description: message, variant: "error" });
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = () => {
    const initial: Message = {
      id: createId("assistant"),
      role: "assistant",
      text: "Historique efface. Je suis pret pour une nouvelle question fiscale.",
      createdAt: new Date().toISOString()
    };
    setMessages([initial]);
    push({ title: "Historique efface", description: "La conversation locale a ete reinitialisee.", variant: "success" });
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between gap-3">
        <div>
          <CardTitle>Assistant Fiscal IA</CardTitle>
          <CardDescription>Questions libres sur CGI, 2058-A, regimes fiscaux et alertes.</CardDescription>
        </div>
        <Button type="button" variant="outline" size="sm" onClick={clearHistory}>
          <RotateCcw className="mr-2 h-4 w-4" />
          Reinitialiser
        </Button>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="max-h-[460px] space-y-3 overflow-y-auto rounded-md border p-3" aria-live="polite">
          {messages.map((message) => (
            <div
              key={message.id}
              className={
                message.role === "assistant"
                  ? "max-w-[92%] rounded-md bg-muted p-3 text-sm"
                  : "ml-auto max-w-[85%] rounded-md bg-primary p-3 text-sm text-primary-foreground"
              }
            >
              <p className="whitespace-pre-wrap">{message.text}</p>
              <p className="mt-2 text-[10px] opacity-75">{new Date(message.createdAt).toLocaleTimeString("fr-FR")}</p>
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
            aria-label="Votre question fiscale"
          />
          <Button type="button" onClick={() => void submit()} disabled={!canSend}>
            <Send className="mr-2 h-4 w-4" />
            {loading ? "Analyse..." : "Envoyer"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
