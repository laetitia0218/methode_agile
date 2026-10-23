# Générateur de documentation projet

MVP étudiant construit avec Streamlit, Gemini API, Pydantic et ReportLab.

## Lancer le projet

```bash
cp .env.example .env
# Ajouter GEMINI_API_KEY dans .env
uv sync
uv run streamlit run app.py
```

L'application permet de saisir un besoin projet, génère une réponse JSON validée,
affiche le backlog et la roadmap, puis produit un PDF téléchargeable.

## Tests

```bash
uv run pytest
```
