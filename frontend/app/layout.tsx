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
          <a
            href="#contenu-principal"
            className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-background focus:px-3 focus:py-2 focus:text-sm"
          >
            Aller au contenu principal
          </a>
          <div className="min-h-screen bg-gradient-to-b from-blue-50/80 via-background to-background dark:from-slate-950 dark:via-background dark:to-background">
            <Header />
            <main id="contenu-principal" className="container-page py-8 md:py-10">
              {children}
            </main>
            <Footer />
          </div>
        </Providers>
      </body>
    </html>
  );
}

