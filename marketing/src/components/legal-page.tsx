import { ReactNode } from "react";

export function LegalPage({
  title,
  lastUpdated,
  children,
}: {
  title: string;
  lastUpdated: string;
  children: ReactNode;
}) {
  return (
    <div className="mx-auto max-w-3xl px-6 py-20">
      <h1 className="text-3xl font-bold tracking-tight mb-2">{title}</h1>
      <p className="text-sm text-slate-400 mb-12">Derniere mise a jour : {lastUpdated}</p>
      <div className="prose prose-slate prose-sm max-w-none [&_h2]:text-xl [&_h2]:font-bold [&_h2]:mt-10 [&_h2]:mb-4 [&_h3]:text-lg [&_h3]:font-semibold [&_h3]:mt-6 [&_h3]:mb-3 [&_p]:text-slate-600 [&_p]:leading-relaxed [&_p]:mb-4 [&_ul]:list-disc [&_ul]:pl-5 [&_ul]:space-y-2 [&_li]:text-slate-600 [&_li]:text-sm [&_a]:text-primary-600 [&_a]:underline">
        {children}
      </div>
    </div>
  );
}
