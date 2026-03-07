"use client";

import { X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useToast } from "@/lib/toast";

export default function Toaster() {
  const { toasts, dismiss } = useToast();

  return (
    <div aria-live="polite" aria-atomic="true" className="pointer-events-none fixed right-4 top-20 z-50 flex w-full max-w-sm flex-col gap-2">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={cn(
            "pointer-events-auto rounded-lg border bg-card p-4 shadow-lg",
            toast.variant === "success" && "border-emerald-300",
            toast.variant === "error" && "border-red-300"
          )}
          role="status"
        >
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-sm font-semibold">{toast.title}</p>
              {toast.description ? <p className="mt-1 text-xs text-muted-foreground">{toast.description}</p> : null}
            </div>
            <Button variant="ghost" size="icon" onClick={() => dismiss(toast.id)} aria-label="Fermer la notification">
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>
      ))}
    </div>
  );
}
