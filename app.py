import os

import streamlit as st
from dotenv import load_dotenv

from gemini_service import generate_document
from models import ProjectDocument
from pdf_service import create_pdf


load_dotenv()

st.set_page_config(
    page_title="Générateur de documentation projet",
    page_icon="📘",
    layout="wide",
)

st.title("Générateur de documentation projet")
st.caption("Décrivez votre idée, puis obtenez un backlog, une architecture et une roadmap en PDF.")

with st.sidebar:
    st.header("Configuration")
    saved_key = os.getenv("GEMINI_API_KEY", "")
    api_key = st.text_input(
        "Clé API Gemini",
        value=saved_key,
        type="password",
        help="La clé reste dans cette session et n'est pas enregistrée par l'application.",
    )
    model = st.selectbox("Modèle", ["gemini-3.8-flash"], index=0)
    team_size = st.number_input("Taille de l'équipe", min_value=1, max_value=10, value=4)
    sprint_duration = st.number_input(
        "Durée d'un sprint (semaines)", min_value=1, max_value=4, value=2
    )

with st.form("project_form"):
    description = st.text_area(
        "Description du projet *",
        height=150,
        placeholder="Exemple : Une application qui transforme la description d'un projet en documentation structurée...",
    )
    left, right = st.columns(2)
    with left:
        objectives = st.text_area(
            "Objectifs",
            placeholder="Réduire le temps de préparation, aider les étudiants...",
        )
        features = st.text_area(
            "Fonctionnalités principales",
            placeholder="Saisie libre, génération Gemini, validation JSON, export PDF...",
        )
    with right:
        constraints = st.text_area(
            "Contraintes",
            placeholder="Python, Streamlit, petite équipe, délai court...",
            height=168,
        )
    submitted = st.form_submit_button("Générer la documentation", type="primary")

if submitted:
    if not description.strip():
        st.error("Ajoutez une description du projet.")
    elif not api_key.strip():
        st.error("Ajoutez votre clé API Gemini dans la barre latérale ou dans le fichier .env.")
    else:
        try:
            with st.spinner("Gemini prépare la documentation..."):
                result = generate_document(
                    api_key=api_key.strip(),
                    model=model,
                    description=description.strip(),
                    objectives=objectives.strip(),
                    features=features.strip(),
                    constraints=constraints.strip(),
                    team_size=int(team_size),
                    sprint_duration=int(sprint_duration),
                )
                st.session_state["document"] = result
                st.session_state["pdf"] = create_pdf(result)
        except Exception as exc:
            st.error(f"La génération a échoué : {exc}")

document: ProjectDocument | None = st.session_state.get("document")
if document:
    st.success("Documentation générée et validée.")
    st.subheader(document.project_title)
    st.write(document.presentation)

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Vue d'ensemble", "Backlog", "Architecture", "Roadmap & tests"]
    )
    with tab1:
        st.markdown("#### Objectifs")
        for objective in document.objectives:
            st.write(f"- {objective}")
        st.markdown("#### Périmètre inclus")
        for item in document.scope.included:
            st.write(f"- {item}")

    with tab2:
        for epic in document.epics:
            with st.expander(epic.name, expanded=True):
                st.write(epic.description)
                for story in epic.user_stories:
                    st.markdown(f"**{story.title}**")
                    st.caption(f"{story.priority} · {story.estimate_points} points")
                    for criterion in story.acceptance_criteria:
                        st.write(f"- [ ] {criterion}")

    with tab3:
        st.write(document.architecture.overview)
        st.dataframe(
            [component.model_dump() for component in document.architecture.components],
            use_container_width=True,
            hide_index=True,
        )
        st.markdown("#### Technologies")
        st.write(" · ".join(document.architecture.technologies))

    with tab4:
        for sprint in document.roadmap:
            st.markdown(f"**{sprint.name} — {sprint.objective}**")
            st.caption(sprint.duration)
            for deliverable in sprint.deliverables:
                st.write(f"- {deliverable}")
        st.markdown("#### Tests")
        st.dataframe(
            [test.model_dump() for test in document.test_strategy],
            use_container_width=True,
            hide_index=True,
        )

    st.download_button(
        "Télécharger le PDF",
        data=st.session_state["pdf"],
        file_name="documentation_projet.pdf",
        mime="application/pdf",
        type="primary",
    )

