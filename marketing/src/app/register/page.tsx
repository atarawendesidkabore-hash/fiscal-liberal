import { AppRedirect } from "@/components/app-redirect";

export default function RegisterPage() {
  return (
    <AppRedirect
      path="/register"
      title="Creation de compte FiscIA Pro"
      description="Redirection vers l'espace d'inscription pour demarrer votre essai et acceder a l'application."
    />
  );
}
