from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, model_validator


ComponentType = Literal["voltage_source", "resistor", "switch"]
AnalysisType = Literal["dc_operating_point"]


class Metadata(BaseModel):
    title: Optional[str] = None
    image_id: Optional[str] = None


class BoundingBox(BaseModel):
    x: float
    y: float
    width: float
    height: float


class DetectionComponent(BaseModel):
    id: str
    type: ComponentType
    bbox: BoundingBox
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    source: str


class DetectionWire(BaseModel):
    id: str
    points: List[List[float]]
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    source: str


class DetectionNode(BaseModel):
    id: str
    x: float
    y: float
    source: str


class DetectionText(BaseModel):
    id: str
    text: str
    bbox: BoundingBox
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    source: str


class DetectionDocument(BaseModel):
    metadata: Metadata = Field(default_factory=Metadata)
    components: List[DetectionComponent] = Field(default_factory=list)
    wires: List[DetectionWire] = Field(default_factory=list)
    nodes: List[DetectionNode] = Field(default_factory=list)
    texts: List[DetectionText] = Field(default_factory=list)


class PhysicsNode(BaseModel):
    id: str


class PhysicsConnection(BaseModel):
    component_id: str
    terminal: str
    node_id: str


class PhysicsComponent(BaseModel):
    id: str
    type: ComponentType
    terminals: List[str]
    value: Optional[float] = None
    source: str
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    bbox: Optional[BoundingBox] = None

    @model_validator(mode="after")
    def validate_value(self) -> "PhysicsComponent":
        if self.type in {"voltage_source", "resistor"} and self.value is None:
            raise ValueError(f"{self.type} requires a numeric value")
        if self.type == "switch" and len(self.terminals) != 2:
            raise ValueError("switch must expose exactly two terminals")
        return self


class SimulationConfig(BaseModel):
    analysis_type: AnalysisType = "dc_operating_point"


class PhysicsJsonDocument(BaseModel):
    metadata: Metadata = Field(default_factory=Metadata)
    components: List[PhysicsComponent]
    nodes: List[PhysicsNode]
    connections: List[PhysicsConnection]
    parameters: Dict[str, Any] = Field(default_factory=dict)
    simulation_config: SimulationConfig = Field(default_factory=SimulationConfig)

    @model_validator(mode="after")
    def validate_topology(self) -> "PhysicsJsonDocument":
        node_ids = {node.id for node in self.nodes}
        component_ids = {component.id for component in self.components}
        for connection in self.connections:
            if connection.node_id not in node_ids:
                raise ValueError(f"Unknown node referenced: {connection.node_id}")
            if connection.component_id not in component_ids:
                raise ValueError(
                    f"Unknown component referenced: {connection.component_id}"
                )
        return self
