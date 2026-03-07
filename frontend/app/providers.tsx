"use client";

import type { ReactNode } from "react";
import { ThemeProvider } from "next-themes";
import { SWRConfig } from "swr";

import Toaster from "@/components/ui/toaster";
import { AuthProvider } from "@/lib/auth";
import { ToastProvider } from "@/lib/toast";

type ProvidersProps = {
  children: ReactNode;
};

export default function Providers({ children }: ProvidersProps) {
  return (
    <ThemeProvider attribute="class" defaultTheme="light" enableSystem disableTransitionOnChange>
      <SWRConfig
        value={{
          revalidateOnFocus: false,
          dedupingInterval: 30_000,
          focusThrottleInterval: 10_000,
          shouldRetryOnError: false
        }}
      >
        <ToastProvider>
          <AuthProvider>
            {children}
            <Toaster />
          </AuthProvider>
        </ToastProvider>
      </SWRConfig>
    </ThemeProvider>
  );
}

