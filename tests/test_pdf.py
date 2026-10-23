from models import ProjectDocument
from pdf_service import create_pdf


def test_pdf_generation() -> None:
    document = ProjectDocument.model_validate(
        {
            "project_title": "Projet étudiant",
            "presentation": "Une application simple de génération documentaire.",
            "objectives": ["Créer un document exploitable"],
            "scope": {"included": ["Saisie du besoin"], "excluded": ["Application mobile"]},
            "functional_requirements": [
                {"name": "Saisie", "description": "Décrire le projet", "priority": "Must"}
            ],
            "non_functional_requirements": [
                {"name": "Simplicité", "description": "Interface claire", "priority": "Must"}
            ],
            "actors": [{"name": "Étudiant", "role": "Crée la documentation"}],
            "use_cases": [
                {"name": "Générer", "actor": "Étudiant", "description": "Générer le document"}
            ],
            "epics": [
                {
                    "name": "Documentation",
                    "description": "Génération du contenu",
                    "user_stories": [
                        {
                            "title": "En tant qu'étudiant, je veux générer un PDF afin de le partager.",
                            "acceptance_criteria": ["Le PDF est téléchargeable"],
                            "priority": "Must",
                            "estimate_points": 3,
                        }
                    ],
                }
            ],
            "architecture": {
                "overview": "Application Streamlit simple.",
                "components": [
                    {"name": "UI", "responsibility": "Saisie", "technology": "Streamlit"}
                ],
                "technologies": ["Python", "Streamlit"],
                "data_model": [{"name": "Projet", "fields": ["titre", "description"]}],
            },
            "roadmap": [
                {
                    "name": "Sprint 1",
                    "objective": "MVP",
                    "duration": "2 semaines",
                    "deliverables": ["Formulaire", "PDF"],
                }
            ],
            "test_strategy": [
                {"name": "Export PDF", "type": "Fonctionnel", "expected_result": "PDF valide"}
            ],
            "risks": [
                {
                    "description": "Réponse API invalide",
                    "impact": "Moyen",
                    "mitigation": "Validation Pydantic",
                }
            ],
        }
    )
    pdf = create_pdf(document)
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 1_000

