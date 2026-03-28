import type { Metadata } from "next";
import { LegalPage } from "@/components/legal-page";

export const metadata: Metadata = {
  title: "Conditions Generales de Vente",
};

export default function CGVPage() {
  return (
    <LegalPage title="Conditions Generales de Vente (CGV)" lastUpdated="1er janvier 2025">
      <h2>1. Objet</h2>
      <p>
        Les presentes Conditions Generales de Vente regissent les relations contractuelles
        entre FiscIA Pro SAS (ci-apres &ldquo;le Prestataire&rdquo;) et tout professionnel
        (ci-apres &ldquo;le Client&rdquo;) souscrivant un abonnement au service FiscIA Pro.
      </p>

      <h2>2. Services proposes</h2>
      <p>Le Prestataire fournit un service en ligne (SaaS) comprenant :</p>
      <ul>
        <li>Un moteur de calcul de l&apos;Impot sur les Societes (Art. 219 CGI)</li>
        <li>Un assistant de determination du resultat fiscal (liasse 2058-A)</li>
        <li>Un verificateur du regime mere-filiale (Art. 145 CGI)</li>
        <li>Une recherche instantanee dans le Code General des Impots</li>
        <li>Un assistant IA fiscal (selon formule souscrite)</li>
      </ul>

      <h2>3. Formules et tarifs</h2>
      <p>Trois formules sont proposees :</p>
      <ul>
        <li><strong>Starter</strong> : 29 EUR HT/mois — 1 utilisateur, 50 calculs/mois</li>
        <li><strong>Pro</strong> : 79 EUR HT/mois — 5 utilisateurs, calculs illimites</li>
        <li><strong>Cabinet</strong> : 199 EUR HT/mois — 20 utilisateurs, API, multi-cabinet</li>
      </ul>
      <p>
        Les prix s&apos;entendent hors taxes. La TVA applicable est celle en vigueur au jour
        de la facturation (20% en France metropolitaine).
      </p>
      <p>
        Tarification annuelle : paiement de 10 mois pour 12 mois d&apos;utilisation
        (soit une remise de 17%).
      </p>

      <h2>4. Essai gratuit</h2>
      <p>
        Chaque nouveau Client beneficie d&apos;un essai gratuit de 14 jours calendaires
        sur la formule Pro. A l&apos;issue de cette periode, le compte passe en lecture seule.
        Les donnees sont conservees pendant 30 jours supplementaires.
        Aucun moyen de paiement n&apos;est requis pour l&apos;essai.
      </p>

      <h2>5. Modalites de paiement</h2>
      <p>
        Le paiement s&apos;effectue par carte bancaire ou prelevement SEPA.
        La facturation est mensuelle ou annuelle selon l&apos;option choisie.
        Les factures sont disponibles dans l&apos;espace Client.
      </p>

      <h2>6. Duree et resiliation</h2>
      <p>
        L&apos;abonnement est a duree indeterminee. Le Client peut resilier
        a tout moment depuis son espace de gestion. La resiliation prend effet
        a la fin de la periode de facturation en cours. Aucun remboursement
        au prorata n&apos;est effectue.
      </p>

      <h2>7. Niveaux de service (SLA)</h2>
      <ul>
        <li>Disponibilite garantie : 99,5% (hors maintenance programmee)</li>
        <li>Maintenance programmee : notifiee 48h a l&apos;avance, en dehors des heures ouvrees</li>
        <li>Support Starter : email, reponse sous 48h ouvrees</li>
        <li>Support Pro : prioritaire, reponse sous 4h ouvrees</li>
        <li>Support Cabinet : telephonique, reponse sous 1h pour les bugs critiques</li>
      </ul>

      <h2>8. Limitation de responsabilite</h2>
      <p>
        Les calculs et informations fournis par FiscIA Pro sont delivres a titre indicatif.
        Ils ne constituent en aucun cas un conseil fiscal personnalise.
        Le Prestataire ne saurait etre tenu responsable des decisions prises
        par le Client sur la base des resultats fournis par le service.
      </p>
      <p>
        La responsabilite du Prestataire est limitee au montant des sommes
        effectivement percues au cours des 12 derniers mois.
      </p>

      <h2>9. Propriete intellectuelle</h2>
      <p>
        Le Client conserve la propriete de toutes les donnees qu&apos;il saisit.
        Le Prestataire conserve la propriete du logiciel, des algorithmes
        et des modeles d&apos;IA. Aucune licence sur le code source n&apos;est concedee
        sauf disposition contraire ecrite.
      </p>

      <h2>10. Protection des donnees</h2>
      <p>
        Le traitement des donnees personnelles est decrit dans la{" "}
        <a href="/confidentialite">Politique de confidentialite</a>.
        Le Prestataire agit en qualite de sous-traitant au sens du RGPD
        pour les donnees clients saisies par le Client.
      </p>

      <h2>11. Droit applicable et juridiction</h2>
      <p>
        Les presentes CGV sont soumises au droit francais.
        Tout litige sera soumis a la competence exclusive des tribunaux de Paris,
        y compris en cas de pluralite de defendeurs ou d&apos;appel en garantie.
      </p>
    </LegalPage>
  );
}
