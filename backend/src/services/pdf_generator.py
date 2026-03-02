"""
Générateur PDF pour les formulaires 2058-A/B/C
Utilise ReportLab pour créer des PDFs conformes au format officiel.
"""

import io
from datetime import date

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from src.database.models import Form2058A, Form2058B, Form2058BItem, Form2058C, Exercice, Company


# Libellés officiels des lignes 2058-A
LIGNES_2058A = [
    ("WA", "Résultat net comptable", "wa_resultat_comptable"),
    # Réintégrations
    ("WB", "Rémunération du travail de l'exploitant ou des associés", "wb_remuneration_exploitant"),
    ("WC", "Part déductible à réintégrer", "wc_part_deductible"),
    ("WD", "Avantages personnels non déductibles (hors amortissements)", "wd_avantages_personnels"),
    ("WE", "Amortissements excédentaires (art. 39-4 CGI)", "we_amortissements_excessifs"),
    ("WF", "Impôt sur les sociétés", "wf_impot_societes"),
    ("WG", "Provisions non déductibles", "wg_provisions_non_deductibles"),
    ("WH", "Amendes et pénalités", "wh_amendes_penalites"),
    ("WI", "Dépenses somptuaires (art. 39-4 CGI)", "wi_charges_somptuaires"),
    ("WJ", "Intérêts excédentaires (art. 212 bis CGI)", "wj_interets_excessifs"),
    ("WK", "Charges à payer non déductibles", "wk_charges_payer_non_deduct"),
    ("WL", "Autres réintégrations", "wl_autres_reintegrations"),
    # Déductions
    ("WM", "Quote-part de résultat en GIE/sociétés de personnes", "wm_quote_part_gie"),
    ("WN", "Produits nets de participations exonérés", "wn_produits_participation"),
    ("WO", "Plus-values à long terme", "wo_plus_values_lt"),
    ("WP", "Fraction des loyers excédentaires", "wp_loyers_excessifs"),
    ("WQ", "Reprises de provisions non déductibles", "wq_reprises_provisions"),
    ("WR", "Autres déductions", "wr_autres_deductions"),
    # Totaux
    ("WS", "TOTAL DES RÉINTÉGRATIONS", "ws_total_reintegrations"),
    ("WT", "TOTAL DES DÉDUCTIONS", "wt_total_deductions"),
    ("WU", "RÉSULTAT FISCAL (Bénéfice ou Déficit)", "wu_resultat_fiscal"),
]


def _fmt(value: float) -> str:
    """Formate un montant en euros."""
    if value == 0:
        return "—"
    return f"{value:,.2f} €".replace(",", " ").replace(".", ",")


def generate_2058a_pdf(
    form: Form2058A,
    exercice: Exercice,
    company: Company,
) -> bytes:
    """Génère le PDF du formulaire 2058-A."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle", parent=styles["Title"], fontSize=14, spaceAfter=6
    )
    header_style = ParagraphStyle(
        "Header", parent=styles["Normal"], fontSize=9, textColor=colors.grey
    )

    elements = []

    # En-tête
    elements.append(Paragraph("FORMULAIRE N° 2058-A", title_style))
    elements.append(Paragraph("DÉTERMINATION DU RÉSULTAT FISCAL", styles["Heading2"]))
    elements.append(Spacer(1, 4 * mm))

    # Info société
    info_data = [
        ["Raison sociale", company.raison_sociale, "SIREN", company.siren or "—"],
        ["Forme juridique", company.forme_juridique, "Exercice",
         f"{exercice.date_debut} au {exercice.date_fin}"],
    ]
    info_table = Table(info_data, colWidths=[35 * mm, 55 * mm, 30 * mm, 55 * mm])
    info_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("BACKGROUND", (0, 0), (0, -1), colors.Color(0.95, 0.95, 0.95)),
        ("BACKGROUND", (2, 0), (2, -1), colors.Color(0.95, 0.95, 0.95)),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 6 * mm))

    # Tableau principal
    table_data = [["Code", "Désignation", "Montant"]]

    for i, (code, label, field) in enumerate(LIGNES_2058A):
        value = getattr(form, field) or 0.0
        table_data.append([code, label, _fmt(value)])

    main_table = Table(table_data, colWidths=[15 * mm, 120 * mm, 40 * mm])

    # Style du tableau
    style_commands = [
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.2, 0.3, 0.5)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
    ]

    # Ligne WA (résultat comptable) — fond bleu clair
    style_commands.append(("BACKGROUND", (0, 1), (-1, 1), colors.Color(0.9, 0.93, 1.0)))

    # Séparation réintégrations / déductions
    # Les réintégrations sont lignes 2-12 (WB-WL), déductions 13-18 (WM-WR)
    # Totaux : WS=19, WT=20, WU=21
    for row_idx in [len(table_data) - 3, len(table_data) - 2, len(table_data) - 1]:
        style_commands.append(("FONTNAME", (0, row_idx), (-1, row_idx), "Helvetica-Bold"))
        style_commands.append(("BACKGROUND", (0, row_idx), (-1, row_idx), colors.Color(0.92, 0.92, 0.92)))

    # Résultat fiscal (dernière ligne) — fond vert/rouge selon bénéfice/déficit
    wu = form.wu_resultat_fiscal or 0.0
    if wu >= 0:
        style_commands.append(("BACKGROUND", (0, len(table_data) - 1), (-1, len(table_data) - 1),
                              colors.Color(0.85, 0.95, 0.85)))
    else:
        style_commands.append(("BACKGROUND", (0, len(table_data) - 1), (-1, len(table_data) - 1),
                              colors.Color(0.95, 0.85, 0.85)))

    main_table.setStyle(TableStyle(style_commands))
    elements.append(main_table)

    # Pied de page
    elements.append(Spacer(1, 8 * mm))
    elements.append(Paragraph(
        f"Généré le {date.today().isoformat()} — Fiscal Liberal v1.0",
        header_style,
    ))

    doc.build(elements)
    return buffer.getvalue()


def generate_2058b_pdf(
    form: Form2058B,
    items: list,
    exercice: Exercice,
    company: Company,
) -> bytes:
    """Génère le PDF du formulaire 2058-B (détail des charges non déductibles)."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=15 * mm, bottomMargin=15 * mm,
                            leftMargin=15 * mm, rightMargin=15 * mm)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("FORMULAIRE N° 2058-B", styles["Title"]))
    elements.append(Paragraph("DÉTAIL DES CHARGES NON DÉDUCTIBLES", styles["Heading2"]))
    elements.append(Spacer(1, 4 * mm))
    elements.append(Paragraph(
        f"{company.raison_sociale} — Exercice {exercice.date_debut} au {exercice.date_fin}",
        styles["Normal"],
    ))
    elements.append(Spacer(1, 6 * mm))

    table_data = [["Nature", "Article CGI", "Montant", "Commentaire"]]
    total = 0.0
    for item in items:
        table_data.append([
            item.nature,
            item.article_cgi or "—",
            _fmt(item.montant),
            item.commentaire or "",
        ])
        total += item.montant

    table_data.append(["TOTAL", "", _fmt(total), ""])

    table = Table(table_data, colWidths=[50 * mm, 30 * mm, 35 * mm, 60 * mm])
    table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.2, 0.3, 0.5)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, -1), (-1, -1), colors.Color(0.92, 0.92, 0.92)),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    elements.append(table)

    doc.build(elements)
    return buffer.getvalue()


def generate_2058c_pdf(
    form: Form2058C,
    exercice: Exercice,
    company: Company,
) -> bytes:
    """Génère le PDF du formulaire 2058-C (affectation du résultat)."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=15 * mm, bottomMargin=15 * mm,
                            leftMargin=15 * mm, rightMargin=15 * mm)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("FORMULAIRE N° 2058-C", styles["Title"]))
    elements.append(Paragraph("AFFECTATION DU RÉSULTAT ET RENSEIGNEMENTS DIVERS", styles["Heading2"]))
    elements.append(Spacer(1, 4 * mm))
    elements.append(Paragraph(
        f"{company.raison_sociale} — Exercice {exercice.date_debut} au {exercice.date_fin}",
        styles["Normal"],
    ))
    elements.append(Spacer(1, 6 * mm))

    lignes = [
        ("Résultat de l'exercice", form.resultat_exercice),
        ("Report à nouveau antérieur", form.report_a_nouveau_anterieur),
        ("Dividendes distribués", form.dividendes_distribues),
        ("Réserves légales", form.reserves_legales),
        ("Réserves statutaires", form.reserves_statutaires),
        ("Autres réserves", form.autres_reserves),
        ("Report à nouveau (nouveau)", form.report_a_nouveau_nouveau),
    ]

    table_data = [["Désignation", "Montant"]]
    for label, value in lignes:
        table_data.append([label, _fmt(value or 0.0)])

    table = Table(table_data, colWidths=[120 * mm, 50 * mm])
    table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.2, 0.3, 0.5)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(table)

    doc.build(elements)
    return buffer.getvalue()
