import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Header } from "@/components/header";
import { Footer } from "@/components/footer";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin", "latin-ext"],
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "FiscIA Pro — L'assistant IA des fiscalistes francais",
    template: "%s | FiscIA Pro",
  },
  description:
    "Preparation 2065 + 2033, liasse 2058-A automatisee, import Excel/PDF et calcul IS dans un meme flux pour les fiscalistes francais.",
  keywords: [
    "fiscaliste",
    "impot societes",
    "IS",
    "2065",
    "2033",
    "Art 219 CGI",
    "liasse 2058-A",
    "expert-comptable",
    "IA fiscale",
    "import excel",
    "import pdf",
    "calcul IS",
    "regime mere-filiale",
    "Art 145 CGI",
  ],
  authors: [{ name: "FiscIA Pro" }],
  openGraph: {
    type: "website",
    locale: "fr_FR",
    url: "https://fiscia.pro",
    siteName: "FiscIA Pro",
    title: "FiscIA Pro — L'assistant IA des fiscalistes francais",
    description:
      "Preparation 2065 + 2033, liasse 2058-A automatisee, import Excel/PDF et calcul IS dans un meme flux.",
  },
  robots: { index: true, follow: true },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body className="bg-white text-slate-900 antialiased">
        <Header />
        <main className="min-h-screen">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
