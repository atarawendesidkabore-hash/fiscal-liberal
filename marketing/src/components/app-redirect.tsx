"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { appHref } from "@/lib/app-url";

export function AppRedirect({
  path,
  title,
  description,
}: {
  path: string;
  title: string;
  description: string;
}) {
  const [targetHref, setTargetHref] = useState(() => appHref(path));

  useEffect(() => {
    const queryString = window.location.search;
    const nextHref = `${appHref(path)}${queryString}`;
    setTargetHref(nextHref);
    window.location.replace(nextHref);
  }, [path]);

  return (
    <section className="bg-gradient-to-b from-primary-50 to-white px-6 py-24">
      <div className="mx-auto max-w-2xl rounded-2xl border border-slate-200 bg-white p-10 text-center shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary-600">
          Espace client
        </p>
        <h1 className="mt-4 text-3xl font-bold tracking-tight text-slate-900">
          {title}
        </h1>
        <p className="mt-4 text-base leading-relaxed text-slate-600">
          {description}
        </p>
        <div className="mt-8 flex flex-col items-center gap-4">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
          <Link
            href={targetHref}
            className="rounded-lg bg-primary-600 px-5 py-3 text-sm font-semibold text-white transition-colors hover:bg-primary-700"
          >
            Continuer maintenant
          </Link>
        </div>
      </div>
    </section>
  );
}
