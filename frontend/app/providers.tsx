"use client";

import type { ReactNode } from "react";
import { ThemeProvider } from "next-themes";

import Toaster from "@/components/ui/toaster";
import { AuthProvider } from "@/lib/auth";
import { ToastProvider } from "@/lib/toast";

type ProvidersProps = {
  children: ReactNode;
};

export default function Providers({ children }: ProvidersProps) {
  return (
    <ThemeProvider attribute="class" defaultTheme="light" enableSystem disableTransitionOnChange>
      <ToastProvider>
        <AuthProvider>
          {children}
          <Toaster />
        </AuthProvider>
      </ToastProvider>
    </ThemeProvider>
  );
}

