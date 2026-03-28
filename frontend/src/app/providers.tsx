"use client";

import { AuthProvider } from "@/lib/auth-context";
import Navbar from "@/components/navbar";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <Navbar />
      <main className="max-w-7xl mx-auto px-4 py-8">{children}</main>
    </AuthProvider>
  );
}
