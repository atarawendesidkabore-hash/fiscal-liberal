"use client";

import { useState } from "react";
import { Section, SectionHeader } from "@/components/section";

const CATEGORIES = [
  { value: "demo", label: "Demande de demo" },
  { value: "commercial", label: "Question commerciale" },
  { value: "support", label: "Support technique" },
  { value: "partenariat", label: "Partenariat" },
  { value: "presse", label: "Presse / Media" },
  { value: "autre", label: "Autre" },
];

export default function ContactPage() {
  const [submitted, setSubmitted] = useState(false);

  return (
    <>
      <Section className="bg-gradient-to-b from-primary-50 to-white pt-12">
        <SectionHeader
          eyebrow="Contact"
          title="Parlons de votre cabinet"
          subtitle="Notre equipe repond sous 24 heures ouvrees. Pour le support technique, le delai moyen est de 4 heures."
        />
      </Section>

      <Section>
        <div className="grid lg:grid-cols-2 gap-16">
          {/* Contact form */}
          <div>
            <h3 className="text-lg font-semibold mb-6">Envoyez-nous un message</h3>
            {submitted ? (
              <div className="rounded-xl bg-green-50 border border-green-200 p-8 text-center">
                <svg className="mx-auto h-12 w-12 text-green-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-lg font-semibold text-green-900">Message envoye !</p>
                <p className="text-sm text-green-700 mt-2">
                  Nous vous repondrons sous 24 heures ouvrees.
                </p>
              </div>
            ) : (
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  setSubmitted(true);
                }}
                className="space-y-5"
              >
                <div className="grid sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Prenom *</label>
                    <input
                      type="text"
                      required
                      className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                      placeholder="Jean"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Nom *</label>
                    <input
                      type="text"
                      required
                      className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                      placeholder="Dupont"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Email professionnel *</label>
                  <input
                    type="email"
                    required
                    className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="jean@cabinet-dupont.fr"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Nom du cabinet</label>
                  <input
                    type="text"
                    className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="Cabinet Dupont & Associes"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Sujet *</label>
                  <select
                    required
                    className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white"
                  >
                    <option value="">Selectionnez un sujet</option>
                    {CATEGORIES.map((c) => (
                      <option key={c.value} value={c.value}>
                        {c.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Message *</label>
                  <textarea
                    required
                    rows={5}
                    className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
                    placeholder="Decrivez votre besoin ou votre question..."
                  />
                </div>

                <button
                  type="submit"
                  className="w-full rounded-lg bg-primary-600 px-6 py-3 text-sm font-semibold text-white hover:bg-primary-700 transition-colors"
                >
                  Envoyer le message
                </button>

                <p className="text-xs text-slate-400">
                  En envoyant ce formulaire, vous acceptez notre{" "}
                  <a href="/confidentialite" className="underline">politique de confidentialite</a>.
                </p>
              </form>
            )}
          </div>

          {/* Contact info */}
          <div className="space-y-8">
            <div>
              <h3 className="text-lg font-semibold mb-6">Coordonnees</h3>
              <div className="space-y-4">
                <div className="flex items-start gap-4">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-100 shrink-0">
                    <svg className="h-5 w-5 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-900">Email</p>
                    <p className="text-sm text-primary-600">contact@fiscia.pro</p>
                    <p className="text-sm text-primary-600">support@fiscia.pro</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-100 shrink-0">
                    <svg className="h-5 w-5 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 6.75c0 8.284 6.716 15 15 15h2.25a2.25 2.25 0 002.25-2.25v-1.372c0-.516-.351-.966-.852-1.091l-4.423-1.106c-.44-.11-.902.055-1.173.417l-.97 1.293c-.282.376-.769.542-1.21.38a12.035 12.035 0 01-7.143-7.143c-.162-.441.004-.928.38-1.21l1.293-.97c.363-.271.527-.734.417-1.173L6.963 3.102a1.125 1.125 0 00-1.091-.852H4.5A2.25 2.25 0 002.25 4.5v2.25z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-900">Telephone</p>
                    <p className="text-sm text-slate-600">01 76 34 00 00</p>
                    <p className="text-xs text-slate-400">Lun-Ven, 9h-18h</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-100 shrink-0">
                    <svg className="h-5 w-5 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-900">Adresse</p>
                    <p className="text-sm text-slate-600">
                      FiscIA Pro SAS<br />
                      42 rue de la Boetie<br />
                      75008 Paris, France
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Response time */}
            <div className="rounded-xl bg-slate-50 border border-slate-200 p-6">
              <h4 className="text-sm font-semibold text-slate-900 mb-3">Temps de reponse</h4>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">Demande commerciale</span>
                  <span className="font-medium text-slate-900">&lt; 24h ouvrees</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">Support technique</span>
                  <span className="font-medium text-slate-900">&lt; 4h (Pro/Cabinet)</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">Bug critique</span>
                  <span className="font-medium text-red-600">&lt; 1h (Cabinet)</span>
                </div>
              </div>
            </div>

            {/* Map placeholder */}
            <div className="rounded-xl bg-slate-200 border border-slate-300 h-64 flex items-center justify-center">
              <p className="text-sm text-slate-500">Carte interactive — 42 rue de la Boetie, 75008 Paris</p>
            </div>
          </div>
        </div>
      </Section>
    </>
  );
}
