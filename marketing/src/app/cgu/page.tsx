import type { Metadata } from "next";
import { LegalPage } from "@/components/legal-page";

export const metadata: Metadata = {
  title: "Conditions Generales d'Utilisation",
};

export default function CGUPage() {
  return (
    <LegalPage title="Conditions Generales d'Utilisation (CGU)" lastUpdated="1er janvier 2025">
      <h2>1. Acceptation des CGU</h2>
      <p>
        L&apos;utilisation du service FiscIA Pro implique l&apos;acceptation pleine et entiere
        des presentes Conditions Generales d&apos;Utilisation. Si vous n&apos;acceptez pas
        ces conditions, vous ne devez pas utiliser le service.
      </p>

      <h2>2. Description du service</h2>
      <p>
        FiscIA Pro est un service en ligne d&apos;aide au calcul de l&apos;Impot sur les Societes
        et de determination du resultat fiscal. Il comprend un moteur de calcul, un assistant
        de liasse 2058-A, un verificateur Art. 145 CGI et un assistant IA fiscal.
      </p>

      <h2>3. Inscription et compte utilisateur</h2>
      <ul>
        <li>L&apos;inscription est reservee aux professionnels (experts-comptables, fiscalistes, avocats fiscalistes)</li>
        <li>Vous devez fournir des informations exactes et a jour</li>
        <li>Vous etes responsable de la confidentialite de vos identifiants</li>
        <li>Un compte ne peut etre partage entre plusieurs personnes physiques</li>
        <li>Vous devez signaler immediatement toute utilisation non autorisee</li>
      </ul>

      <h2>4. Utilisation du service</h2>
      <h3>4.1 Utilisation autorisee</h3>
      <ul>
        <li>Calcul de l&apos;IS pour vos clients ou votre entreprise</li>
        <li>Recherche d&apos;articles du CGI dans le cadre de votre activite professionnelle</li>
        <li>Utilisation de l&apos;assistant IA pour des questions fiscales IS</li>
      </ul>

      <h3>4.2 Utilisation interdite</h3>
      <ul>
        <li>Utiliser le service pour des activites illegales ou frauduleuses</li>
        <li>Tenter de contourner les mesures de securite</li>
        <li>Effectuer du reverse engineering sur le logiciel ou les modeles IA</li>
        <li>Utiliser des robots ou scripts automatises pour acceder au service</li>
        <li>Partager vos identifiants avec des tiers</li>
        <li>Utiliser le service au-dela des limites de votre formule</li>
      </ul>

      <h2>5. Nature indicative des resultats</h2>
      <p>
        <strong>IMPORTANT</strong> : Les calculs, analyses et recommandations fournis par
        FiscIA Pro sont delivres a titre strictement indicatif. Ils ne constituent pas
        un conseil fiscal personnalise et ne sauraient se substituer a l&apos;avis d&apos;un
        professionnel qualifie.
      </p>
      <p>
        Chaque resultat est accompagne du disclaimer suivant :<br />
        <em>
          &ldquo;Reponse indicative. Toute decision fiscale engageante necessite l&apos;analyse
          personnalisee d&apos;un professionnel qualifie.&rdquo;
        </em>
      </p>

      <h2>6. Disponibilite du service</h2>
      <p>
        FiscIA Pro s&apos;efforce de maintenir le service disponible 24h/24, 7j/7.
        Toutefois, le Prestataire ne garantit pas l&apos;absence d&apos;interruptions dues a :
      </p>
      <ul>
        <li>Operations de maintenance (notifiees 48h a l&apos;avance)</li>
        <li>Defaillance des reseaux de telecommunication</li>
        <li>Cas de force majeure</li>
      </ul>

      <h2>7. Propriete des donnees</h2>
      <p>
        Vous restez proprietaire de toutes les donnees que vous saisissez dans FiscIA Pro.
        Le Prestataire ne revendique aucun droit de propriete sur vos donnees.
        Vous pouvez a tout moment exporter vos donnees via l&apos;endpoint GDPR
        ou demander leur suppression integrale.
      </p>

      <h2>8. Suspension et resiliation</h2>
      <p>
        Le Prestataire se reserve le droit de suspendre ou resilier votre compte en cas de :
      </p>
      <ul>
        <li>Violation des presentes CGU</li>
        <li>Utilisation abusive du service (surcharge volontaire, scraping)</li>
        <li>Non-paiement des sommes dues</li>
        <li>Demande d&apos;une autorite judiciaire</li>
      </ul>

      <h2>9. Modification des CGU</h2>
      <p>
        Le Prestataire se reserve le droit de modifier les presentes CGU.
        Les utilisateurs seront informes par email 30 jours avant l&apos;entree en vigueur
        des modifications. La poursuite de l&apos;utilisation du service apres cette date
        vaut acceptation des nouvelles conditions.
      </p>

      <h2>10. Droit applicable</h2>
      <p>
        Les presentes CGU sont soumises au droit francais.
        Tout litige sera soumis aux tribunaux competents de Paris.
      </p>
    </LegalPage>
  );
}
