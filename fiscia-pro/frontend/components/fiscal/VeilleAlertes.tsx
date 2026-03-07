export default function VeilleAlertes() {
  return (
    <div className="rounded bg-white p-4 shadow-sm">
      <h3 className="mb-2 font-semibold">Veille fiscale</h3>
      <ul className="list-disc space-y-1 pl-5 text-sm">
        <li>CRITIQUE: verifier la derniere LFI/LFR.</li>
        <li>IMPORTANT: nouvelles instructions BOFiP a qualifier.</li>
        <li>A SURVEILLER: jurisprudence recente Conseil d&apos;Etat.</li>
      </ul>
    </div>
  );
}

