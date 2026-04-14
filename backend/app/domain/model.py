from pydantic import BaseModel


class PhysicsModel(BaseModel):
    model_type: str
    core_relations: list[str] = []
    variables: list[str] = []
    reasoning_focus: list[str] = []

