export default function RegisterPage() {
  return (
    <main className="mx-auto max-w-md px-6 py-12">
      <h1 className="text-2xl font-bold">Creation de compte</h1>
      <form className="mt-4 space-y-3 rounded bg-white p-4 shadow-sm">
        <input className="w-full rounded border p-2" placeholder="Nom complet" />
        <input className="w-full rounded border p-2" type="email" placeholder="Email" />
        <input className="w-full rounded border p-2" type="password" placeholder="Mot de passe" />
        <button type="button" className="w-full rounded bg-fiscal-500 px-3 py-2 text-white">
          Creer le compte
        </button>
      </form>
    </main>
  );
}

