from google import genai
from google.genai import types

from models import ProjectDocument


SYSTEM_INSTRUCTIONS = """
Tu es un chef de projet logiciel expérimenté. Tu transformes les informations
fournies en documentation claire, réaliste et directement exploitable par une
petite équipe d'étudiants. Évite le jargon et les fonctionnalités inutiles.

Règles importantes :
- Réponds en français.
- N'invente pas de contraintes métier critiques non mentionnées.
- Propose un MVP raisonnable, puis des améliorations simples.
- Les user stories suivent : En tant que..., je veux..., afin de...
- Chaque user story a 2 à 4 critères d'acceptation testables.
- Utilise les priorités Must, Should ou Could et des estimations 1, 2, 3, 5, 8 ou 13.
- La roadmap doit contenir des sprints cohérents avec les user stories.
- La stratégie de test et les risques doivent rester concrets et courts.
""".strip()


def build_prompt(
    description: str,
    objectives: str,
    features: str,
    constraints: str,
    team_size: int,
    sprint_duration: int,
) -> str:
    return f"""
{SYSTEM_INSTRUCTIONS}

Informations du projet :
- Description : {description}
- Objectifs : {objectives or "À déduire prudemment de la description"}
- Fonctionnalités souhaitées : {features or "À proposer pour un MVP"}
- Contraintes : {constraints or "Aucune contrainte supplémentaire indiquée"}
- Taille de l'équipe : {team_size} personne(s)
- Durée souhaitée d'un sprint : {sprint_duration} semaine(s)

Génère la documentation complète selon le schéma demandé. Pour l'architecture,
privilégie Python, Streamlit, Gemini API, JSON/Pydantic et ReportLab lorsque ces
technologies conviennent au besoin décrit.
""".strip()


def generate_document(
    *,
    api_key: str,
    model: str,
    description: str,
    objectives: str,
    features: str,
    constraints: str,
    team_size: int,
    sprint_duration: int,
) -> ProjectDocument:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=build_prompt(
            description,
            objectives,
            features,
            constraints,
            team_size,
            sprint_duration,
        ),
        config=types.GenerateContentConfig(
            temperature=0.3,
            response_mime_type="application/json",
            response_schema=ProjectDocument,
        ),
    )
    if not response.text:
        raise ValueError("Gemini n'a retourné aucun contenu.")
    return ProjectDocument.model_validate_json(response.text)

