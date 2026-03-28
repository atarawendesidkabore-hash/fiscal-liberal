import type { Metadata } from "next";
import { LegalPage } from "@/components/legal-page";

export const metadata: Metadata = {
  title: "Politique de confidentialite",
};

export default function ConfidentialitePage() {
  return (
    <LegalPage title="Politique de confidentialite" lastUpdated="1er janvier 2025">
      <h2>1. Responsable du traitement</h2>
      <p>
        FiscIA Pro SAS, 42 rue de la Boetie, 75008 Paris.<br />
        DPO : dpo@fiscia.pro
      </p>

      <h2>2. Donnees collectees</h2>
      <h3>2.1 Donnees d&apos;inscription</h3>
      <ul>
        <li>Nom, prenom, adresse email professionnelle</li>
        <li>Nom du cabinet, SIREN</li>
        <li>Mot de passe (stocke sous forme de hash bcrypt, jamais en clair)</li>
      </ul>

      <h3>2.2 Donnees de calcul</h3>
      <ul>
        <li>Donnees de liasse 2058-A saisies (benefice, charges, reintegrations)</li>
        <li>Resultats des calculs IS</li>
        <li>SIREN des entreprises clientes (pour le suivi des calculs)</li>
      </ul>

      <h3>2.3 Donnees techniques</h3>
      <ul>
        <li>Adresse IP (journaux d&apos;acces)</li>
        <li>Type de navigateur et systeme d&apos;exploitation</li>
        <li>Horodatage des connexions</li>
      </ul>

      <h2>3. Finalites du traitement</h2>
      <ul>
        <li><strong>Execution du contrat</strong> : fourniture du service de calcul IS</li>
        <li><strong>Securite</strong> : detection des acces non autorises</li>
        <li><strong>Amelioration du service</strong> : statistiques d&apos;utilisation anonymisees</li>
        <li><strong>Communication</strong> : envoi d&apos;informations sur le service (avec consentement)</li>
      </ul>

      <h2>4. Base legale</h2>
      <p>
        Article 6 du RGPD : execution du contrat (Art. 6.1.b), interet legitime pour la securite (Art. 6.1.f),
        consentement pour les communications marketing (Art. 6.1.a).
      </p>

      <h2>5. Duree de conservation</h2>
      <ul>
        <li><strong>Donnees de calcul</strong> : 3 ans (obligation comptable minimale)</li>
        <li><strong>Journaux d&apos;audit</strong> : 3 ans</li>
        <li><strong>Donnees de compte</strong> : duree du contrat + 3 ans apres resiliation</li>
        <li><strong>Logs techniques</strong> : 12 mois</li>
      </ul>

      <h2>6. Destinataires</h2>
      <p>
        Vos donnees ne sont jamais vendues ni partagees a des fins commerciales.
        Les seuls destinataires sont :
      </p>
      <ul>
        <li>L&apos;equipe FiscIA Pro (acces restreint par role)</li>
        <li>Notre hebergeur Scaleway (sous-traitant, DPA signe)</li>
        <li>Autorites competentes si requis par la loi</li>
      </ul>

      <h2>7. IA locale</h2>
      <p>
        Si vous utilisez la fonctionnalite d&apos;IA locale (Ollama), aucune donnee de calcul
        n&apos;est transmise a un serveur externe. Le modele s&apos;execute integralement sur
        votre infrastructure. FiscIA Pro ne collecte que les metriques d&apos;utilisation
        anonymisees (nombre de requetes, temps de reponse) avec votre consentement.
      </p>

      <h2>8. Transferts hors UE</h2>
      <p>
        Aucune donnee personnelle n&apos;est transferee en dehors de l&apos;Union europeenne.
        Toutes les donnees sont hebergees en France (Scaleway DC5, Paris).
      </p>

      <h2>9. Vos droits</h2>
      <p>Conformement au RGPD (Art. 15 a 22), vous disposez des droits suivants :</p>
      <ul>
        <li><strong>Acces</strong> (Art. 15) : obtenir une copie de vos donnees</li>
        <li><strong>Rectification</strong> (Art. 16) : corriger des donnees inexactes</li>
        <li><strong>Effacement</strong> (Art. 17) : demander la suppression de vos donnees</li>
        <li><strong>Portabilite</strong> (Art. 20) : recevoir vos donnees dans un format structure</li>
        <li><strong>Opposition</strong> (Art. 21) : vous opposer au traitement</li>
        <li><strong>Limitation</strong> (Art. 18) : limiter le traitement</li>
      </ul>
      <p>
        Pour exercer ces droits : dpo@fiscia.pro ou via l&apos;endpoint <code>/gdpr/export</code>
        et <code>/gdpr/delete-me</code> dans l&apos;application.
      </p>

      <h2>10. Cookies</h2>
      <p>
        Nous utilisons uniquement des cookies strictement necessaires au fonctionnement
        du service (session d&apos;authentification). Aucun cookie publicitaire ou analytique
        tiers n&apos;est depose sans votre consentement prealable.
      </p>

      <h2>11. Reclamation</h2>
      <p>
        Si vous estimez que le traitement de vos donnees constitue une violation du RGPD,
        vous pouvez introduire une reclamation aupres de la CNIL (www.cnil.fr).
      </p>
    </LegalPage>
  );
}
