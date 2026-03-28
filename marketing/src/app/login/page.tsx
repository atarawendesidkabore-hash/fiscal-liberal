import { AppRedirect } from "@/components/app-redirect";

export default function LoginPage() {
  return (
    <AppRedirect
      path="/login"
      title="Connexion a FiscIA Pro"
      description="Redirection vers l'application securisee pour acceder a votre tableau de bord."
    />
  );
}
