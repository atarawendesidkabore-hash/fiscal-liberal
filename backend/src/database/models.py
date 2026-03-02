from datetime import date, datetime

from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, Text, ForeignKey, Enum
)
from sqlalchemy.orm import relationship

from src.database.connection import Base


# --------------------------------------------------------------------------- #
#  User
# --------------------------------------------------------------------------- #
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    companies = relationship("Company", back_populates="owner")
    audit_logs = relationship("AuditLog", back_populates="user")


# --------------------------------------------------------------------------- #
#  Company — société d'exercice libéral
# --------------------------------------------------------------------------- #
class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    raison_sociale = Column(String(255), nullable=False)
    forme_juridique = Column(
        Enum("SELARL", "SELAS", "SAS", "SARL", "EI", "EURL", name="forme_juridique_enum"),
        nullable=False,
    )
    siren = Column(String(9))
    siret = Column(String(14))
    code_ape = Column(String(10))
    adresse = Column(Text)
    capital_social = Column(Float, default=0.0)
    date_creation = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="companies")
    exercices = relationship("Exercice", back_populates="company", cascade="all, delete-orphan")


# --------------------------------------------------------------------------- #
#  Exercice — année fiscale
# --------------------------------------------------------------------------- #
class Exercice(Base):
    __tablename__ = "exercices"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    cloture = Column(Date)
    statut = Column(
        Enum("brouillon", "valide", "depose", name="statut_exercice_enum"),
        default="brouillon",
    )
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="exercices")
    form_2058a = relationship("Form2058A", back_populates="exercice", uselist=False, cascade="all, delete-orphan")
    form_2058b = relationship("Form2058B", back_populates="exercice", uselist=False, cascade="all, delete-orphan")
    form_2058c = relationship("Form2058C", back_populates="exercice", uselist=False, cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="exercice")


# --------------------------------------------------------------------------- #
#  Form 2058-A — Détermination du résultat fiscal
# --------------------------------------------------------------------------- #
class Form2058A(Base):
    __tablename__ = "form_2058a"

    id = Column(Integer, primary_key=True, index=True)
    exercice_id = Column(Integer, ForeignKey("exercices.id"), unique=True, nullable=False)

    # Ligne de départ
    wa_resultat_comptable = Column(Float, default=0.0)

    # Réintégrations
    wb_remuneration_exploitant = Column(Float, default=0.0)
    wc_part_deductible = Column(Float, default=0.0)
    wd_avantages_personnels = Column(Float, default=0.0)
    we_amortissements_excessifs = Column(Float, default=0.0)
    wf_impot_societes = Column(Float, default=0.0)
    wg_provisions_non_deductibles = Column(Float, default=0.0)
    wh_amendes_penalites = Column(Float, default=0.0)
    wi_charges_somptuaires = Column(Float, default=0.0)
    wj_interets_excessifs = Column(Float, default=0.0)
    wk_charges_payer_non_deduct = Column(Float, default=0.0)
    wl_autres_reintegrations = Column(Float, default=0.0)

    # Déductions
    wm_quote_part_gie = Column(Float, default=0.0)
    wn_produits_participation = Column(Float, default=0.0)
    wo_plus_values_lt = Column(Float, default=0.0)
    wp_loyers_excessifs = Column(Float, default=0.0)
    wq_reprises_provisions = Column(Float, default=0.0)
    wr_autres_deductions = Column(Float, default=0.0)

    # Totaux (calculés par fiscal_engine)
    ws_total_reintegrations = Column(Float, default=0.0)
    wt_total_deductions = Column(Float, default=0.0)
    wu_resultat_fiscal = Column(Float, default=0.0)

    # Méta
    notes = Column(Text, default="")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    exercice = relationship("Exercice", back_populates="form_2058a")


# --------------------------------------------------------------------------- #
#  Form 2058-B — Détail des charges non déductibles
# --------------------------------------------------------------------------- #
class Form2058B(Base):
    __tablename__ = "form_2058b"

    id = Column(Integer, primary_key=True, index=True)
    exercice_id = Column(Integer, ForeignKey("exercices.id"), unique=True, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    exercice = relationship("Exercice", back_populates="form_2058b")
    items = relationship("Form2058BItem", back_populates="form_2058b", cascade="all, delete-orphan")


class Form2058BItem(Base):
    __tablename__ = "form_2058b_items"

    id = Column(Integer, primary_key=True, index=True)
    form_2058b_id = Column(Integer, ForeignKey("form_2058b.id"), nullable=False)
    nature = Column(String(255), nullable=False)
    montant = Column(Float, nullable=False, default=0.0)
    article_cgi = Column(String(50))
    commentaire = Column(Text, default="")

    form_2058b = relationship("Form2058B", back_populates="items")


# --------------------------------------------------------------------------- #
#  Form 2058-C — Affectation du résultat
# --------------------------------------------------------------------------- #
class Form2058C(Base):
    __tablename__ = "form_2058c"

    id = Column(Integer, primary_key=True, index=True)
    exercice_id = Column(Integer, ForeignKey("exercices.id"), unique=True, nullable=False)

    resultat_exercice = Column(Float, default=0.0)
    report_a_nouveau_anterieur = Column(Float, default=0.0)
    dividendes_distribues = Column(Float, default=0.0)
    reserves_legales = Column(Float, default=0.0)
    reserves_statutaires = Column(Float, default=0.0)
    autres_reserves = Column(Float, default=0.0)
    report_a_nouveau_nouveau = Column(Float, default=0.0)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    exercice = relationship("Exercice", back_populates="form_2058c")


# --------------------------------------------------------------------------- #
#  AuditLog — journal des modifications
# --------------------------------------------------------------------------- #
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercice_id = Column(Integer, ForeignKey("exercices.id"), nullable=True)
    form_type = Column(String(20))  # "2058A", "2058B", "2058C"
    field_changed = Column(String(100))
    old_value = Column(String(255))
    new_value = Column(String(255))
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45))

    user = relationship("User", back_populates="audit_logs")
    exercice = relationship("Exercice", back_populates="audit_logs")
