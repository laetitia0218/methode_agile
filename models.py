from typing import Literal

from pydantic import BaseModel, Field


Priority = Literal["Must", "Should", "Could"]


class Scope(BaseModel):
    included: list[str] = Field(description="Éléments inclus dans le périmètre")
    excluded: list[str] = Field(description="Éléments explicitement hors périmètre")


class Requirement(BaseModel):
    name: str
    description: str
    priority: Priority


class Actor(BaseModel):
    name: str
    role: str


class UseCase(BaseModel):
    name: str
    actor: str
    description: str


class UserStory(BaseModel):
    title: str = Field(description="Phrase au format En tant que..., je veux..., afin de...")
    acceptance_criteria: list[str]
    priority: Priority
    estimate_points: int = Field(ge=1, le=13)


class Epic(BaseModel):
    name: str
    description: str
    user_stories: list[UserStory]


class Component(BaseModel):
    name: str
    responsibility: str
    technology: str


class DataEntity(BaseModel):
    name: str
    fields: list[str]


class TechnicalArchitecture(BaseModel):
    overview: str
    components: list[Component]
    technologies: list[str]
    data_model: list[DataEntity]


class Sprint(BaseModel):
    name: str
    objective: str
    duration: str
    deliverables: list[str]


class TestCase(BaseModel):
    name: str
    type: Literal["Unitaire", "Intégration", "Fonctionnel", "Acceptation"]
    expected_result: str


class Risk(BaseModel):
    description: str
    impact: Literal["Faible", "Moyen", "Élevé"]
    mitigation: str


class ProjectDocument(BaseModel):
    project_title: str
    presentation: str
    objectives: list[str]
    scope: Scope
    functional_requirements: list[Requirement]
    non_functional_requirements: list[Requirement]
    actors: list[Actor]
    use_cases: list[UseCase]
    epics: list[Epic]
    architecture: TechnicalArchitecture
    roadmap: list[Sprint]
    test_strategy: list[TestCase]
    risks: list[Risk]

