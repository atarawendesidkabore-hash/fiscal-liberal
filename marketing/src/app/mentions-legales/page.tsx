import type { Metadata } from "next";
import { LegalPage } from "@/components/legal-page";

export const metadata: Metadata = {
  title: "Mentions legales",
};

export default function MentionsLegalesPage() {
  return (
    <LegalPage title="Mentions legales" lastUpdated="1er janvier 2025">
      <h2>1. Editeur du site</h2>
      <p>
        FiscIA Pro SAS<br />
        Societe par actions simplifiee au capital de 50 000 EUR<br />
        Siege social : 42 rue de la Boetie, 75008 Paris<br />
        RCS Paris 123 456 789<br />
        SIRET : 123 456 789 00010<br />
        TVA intracommunautaire : FR 12 123456789
      </p>
      <p>
        Directeur de la publication : Thomas Lefebvre, President<br />
        Email : contact@fiscia.pro<br />
        Telephone : 01 76 34 00 00
      </p>

      <h2>2. Hebergement</h2>
      <p>
        Le site fiscia.pro et l&apos;application FiscIA Pro sont heberges par :<br />
        Scaleway SAS<br />
        8 rue de la Ville l&apos;Eveque, 75008 Paris<br />
        Datacenter : DC5 Paris, France<br />
        Telephone : 01 84 13 00 00
      </p>

      <h2>3. Propriete intellectuelle</h2>
      <p>
        L&apos;ensemble des contenus de ce site (textes, images, logiciels, bases de donnees,
        marques, logos) est la propriete exclusive de FiscIA Pro SAS ou de ses partenaires.
        Toute reproduction, representation, modification ou exploitation, meme partielle,
        est interdite sans autorisation prealable ecrite.
      </p>

      <h2>4. Donnees personnelles</h2>
      <p>
        Le traitement des donnees personnelles est decrit dans notre{" "}
        <a href="/confidentialite">Politique de confidentialite</a>.
        Conformement au RGPD, vous disposez d&apos;un droit d&apos;acces, de rectification,
        de suppression et de portabilite de vos donnees.
      </p>
      <p>
        Delegue a la protection des donnees : dpo@fiscia.pro
      </p>

      <h2>5. Cookies</h2>
      <p>
        Ce site utilise des cookies strictement necessaires au fonctionnement du service.
        Aucun cookie publicitaire ou de suivi tiers n&apos;est utilise sans votre consentement
        explicite. Voir notre politique de cookies dans la{" "}
        <a href="/confidentialite">Politique de confidentialite</a>.
      </p>

      <h2>6. Limitation de responsabilite</h2>
      <p>
        Les calculs et informations fournis par FiscIA Pro sont delivres a titre indicatif.
        Ils ne constituent pas un conseil fiscal personnalise et ne sauraient engager
        la responsabilite de FiscIA Pro SAS. Toute decision fiscale engageante necessite
        l&apos;analyse personnalisee d&apos;un professionnel qualifie.
      </p>

      <h2>7. Droit applicable</h2>
      <p>
        Les presentes mentions legales sont regies par le droit francais.
        En cas de litige, les tribunaux de Paris seront seuls competents.
      </p>
    </LegalPage>
  );
}
