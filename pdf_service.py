from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from models import ProjectDocument


def _safe(value: object) -> str:
    return escape(str(value))


def _page_number(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawRightString(A4[0] - 1.5 * cm, 1 * cm, f"Page {doc.page}")
    canvas.restoreState()


def create_pdf(data: ProjectDocument) -> bytes:
    output = BytesIO()
    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title=data.project_title,
        author="Générateur de documentation projet",
    )

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="TitleBlue",
            parent=styles["Title"],
            textColor=colors.HexColor("#1d4ed8"),
            alignment=TA_CENTER,
            spaceAfter=18,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Section",
            parent=styles["Heading2"],
            textColor=colors.HexColor("#1e3a8a"),
            spaceBefore=12,
            spaceAfter=7,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Small",
            parent=styles["BodyText"],
            fontSize=8.5,
            leading=11,
        )
    )

    story: list[object] = [
        Spacer(1, 1.5 * cm),
        Paragraph(_safe(data.project_title), styles["TitleBlue"]),
        Paragraph("Documentation de planification et de conception", styles["Heading3"]),
        Spacer(1, 0.5 * cm),
        Paragraph(_safe(data.presentation), styles["BodyText"]),
        PageBreak(),
    ]

    def section(title: str) -> None:
        story.append(Paragraph(_safe(title), styles["Section"]))

    def bullets(items: list[str]) -> None:
        for item in items:
            story.append(Paragraph(f"• {_safe(item)}", styles["BodyText"]))
        story.append(Spacer(1, 6))

    def table(headers: list[str], rows: list[list[object]], widths=None) -> None:
        formatted = [[Paragraph(_safe(cell), styles["Small"]) for cell in headers]]
        formatted.extend(
            [Paragraph(_safe(cell), styles["Small"]) for cell in row] for row in rows
        )
        item = Table(formatted, colWidths=widths, repeatRows=1, hAlign="LEFT")
        item.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#94a3b8")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.extend([item, Spacer(1, 8)])

    section("1. Objectifs")
    bullets(data.objectives)

    section("2. Périmètre")
    story.append(Paragraph("Inclus", styles["Heading3"]))
    bullets(data.scope.included)
    story.append(Paragraph("Hors périmètre", styles["Heading3"]))
    bullets(data.scope.excluded)

    section("3. Besoins fonctionnels")
    table(
        ["Besoin", "Description", "Priorité"],
        [[r.name, r.description, r.priority] for r in data.functional_requirements],
        [4.2 * cm, 9.5 * cm, 2.2 * cm],
    )

    section("4. Besoins non fonctionnels")
    table(
        ["Besoin", "Description", "Priorité"],
        [[r.name, r.description, r.priority] for r in data.non_functional_requirements],
        [4.2 * cm, 9.5 * cm, 2.2 * cm],
    )

    section("5. Acteurs et cas d'utilisation")
    table(["Acteur", "Rôle"], [[a.name, a.role] for a in data.actors], [5 * cm, 11 * cm])
    table(
        ["Cas d'utilisation", "Acteur", "Description"],
        [[u.name, u.actor, u.description] for u in data.use_cases],
        [4.5 * cm, 3.5 * cm, 8 * cm],
    )

    section("6. Epics et user stories")
    for epic in data.epics:
        story.append(Paragraph(_safe(epic.name), styles["Heading3"]))
        story.append(Paragraph(_safe(epic.description), styles["BodyText"]))
        rows = []
        for user_story in epic.user_stories:
            criteria = " • ".join(user_story.acceptance_criteria)
            rows.append(
                [
                    user_story.title,
                    criteria,
                    user_story.priority,
                    user_story.estimate_points,
                ]
            )
        table(
            ["User story", "Critères d'acceptation", "Priorité", "Points"],
            rows,
            [6 * cm, 6.5 * cm, 2 * cm, 1.5 * cm],
        )

    section("7. Architecture technique")
    story.append(Paragraph(_safe(data.architecture.overview), styles["BodyText"]))
    table(
        ["Composant", "Responsabilité", "Technologie"],
        [[c.name, c.responsibility, c.technology] for c in data.architecture.components],
        [4 * cm, 7.5 * cm, 4.5 * cm],
    )
    story.append(Paragraph("Technologies proposées", styles["Heading3"]))
    bullets(data.architecture.technologies)
    table(
        ["Entité", "Champs principaux"],
        [[e.name, ", ".join(e.fields)] for e in data.architecture.data_model],
        [5 * cm, 11 * cm],
    )

    section("8. Roadmap")
    table(
        ["Sprint", "Objectif", "Durée", "Livrables"],
        [[s.name, s.objective, s.duration, " • ".join(s.deliverables)] for s in data.roadmap],
        [2.5 * cm, 5 * cm, 2.5 * cm, 6 * cm],
    )

    section("9. Stratégie de tests")
    table(
        ["Test", "Type", "Résultat attendu"],
        [[t.name, t.type, t.expected_result] for t in data.test_strategy],
        [5 * cm, 3 * cm, 8 * cm],
    )

    section("10. Risques et mesures")
    table(
        ["Risque", "Impact", "Mesure"],
        [[r.description, r.impact, r.mitigation] for r in data.risks],
        [6 * cm, 2.5 * cm, 7.5 * cm],
    )

    document.build(story, onFirstPage=_page_number, onLaterPages=_page_number)
    return output.getvalue()

