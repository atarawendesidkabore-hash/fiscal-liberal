"""DGFiP 2058-A model for extra-accounting fiscal result determination."""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, utcnow

MONEY = Numeric(15, 2)


class Liasse2058A(Base):
    """
    Modèle complet du formulaire DGFiP 2058-A.
    Détermination du résultat fiscal (Art. 53 A CGI).
    """

    __tablename__ = "liasse_2058a"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dossier_client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dossiers.id"),
        nullable=False,
    )
    exercice_clos: Mapped[date] = mapped_column(Date, nullable=False)
    designation_entreprise: Mapped[str | None] = mapped_column(String(200), nullable=True)
    siren: Mapped[str | None] = mapped_column(String(9), nullable=True)

    # Données de qualification IS PME
    ca_ht: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    capital_75pct_pp: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Section I - Réintégrations
    WA_benefice_comptable: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    WQ_perte_comptable: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    WB_remuneration_exploitant: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    WC_avantages_personnels: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    WD_amortissements_excedentaires: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    WE_charges_somptuaires: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    WF_taxe_vehicules_societe: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    WG_amendes_penalites: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    WI_is_et_ifa: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    WJ_pv_exercices_anterieurs: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    WK_provisions_non_deductibles: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    K7_qp_pertes_soc_personnes_gie: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    WL_benefices_soc_personnes_gie: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    WM_interets_excedentaires: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    WN_reintegrations_diverses: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    WO_ecarts_opcvm_reintegration: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    L7_resultats_art209B: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)

    XR_total_I: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)

    # Section II - Déductions
    WR_mv_lt_taux_15_8_0: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    L2_pv_lt_imposees_15pct: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    L3_pv_lt_imputees_mv_ant: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    L4_pv_lt_imposees_8pct: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    L5_pv_lt_imputees_deficits: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    WS_pv_ct_imposition_differee: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    WT_pv_regime_fusions: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    WU_ecarts_opcvm_deduction: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    WV_regime_mere_filiale: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    L6_produit_net_qp_frais: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    L8_qp_5pct_pv_taux_zero: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    WW_zones_entreprises_exonerees: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    XB_deductions_diverses: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    WZ_majoration_amortissement: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    XA_investissements_outremer: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    L9_abattements_exonerations: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)

    ZY_total_II: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)

    # Section III - Régimes particuliers
    XD_entreprises_nouvelles_44sexies: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    XF_reprise_difficultes_44septies: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    XS_corse_208quatera: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    XG_zf_corse_44decies: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    XJ_zfu_44octies_44octiesA: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    XL_jei_44sexiesA: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    XO_pole_competitivite_44undecies: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    XH_siic_208c: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)

    # Résultat final
    ZI_rf_avant_regimes: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    ZL_deficit_reporte_arriere: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    XI_deficits_anterieurs_imputes: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    XN_rf_benefice: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)
    XO_rf_deficit: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0"), nullable=False)

    # Métadonnées IA
    ai_anomalies: Mapped[list] = mapped_column(JSONB, default=list)
    ai_suggestions: Mapped[list] = mapped_column(JSONB, default=list)
    is_valide_fiscaliste: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

