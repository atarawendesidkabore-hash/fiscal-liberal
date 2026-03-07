"use client";

import type { ReactNode } from "react";
import { ThemeProvider } from "next-themes";

import { AuthProvider } from "@/lib/auth";

type ProvidersProps = {
  children: ReactNode;
};

export default function Providers({ children }: ProvidersProps) {
  return (
    <ThemeProvider attribute="class" defaultTheme="light" enableSystem disableTransitionOnChange>
      <AuthProvider>{children}</AuthProvider>
    </ThemeProvider>
  );
}

