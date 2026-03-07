import type { Metadata } from "next";
import type { ReactNode } from "react";

import "@/app/globals.css";
import Footer from "@/components/layout/Footer";
import Header from "@/components/layout/Header";

import Providers from "./providers";

export const metadata: Metadata = {
  title: "FiscIA Pro",
  description: "Assistant fiscal IA pour experts-comptables et fiscalistes en France"
};

export default function RootLayout({
  children
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="fr">
      <body>
        <Providers>
          <div className="min-h-screen bg-gradient-to-b from-blue-50/80 via-background to-background dark:from-slate-950 dark:via-background dark:to-background">
            <Header />
            <main className="container-page py-8 md:py-10">{children}</main>
            <Footer />
          </div>
        </Providers>
      </body>
    </html>
  );
}

