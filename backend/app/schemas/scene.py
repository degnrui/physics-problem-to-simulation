from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


SceneComponentType = Literal[
    "battery",
    "switch",
    "resistor",
    "rheostat",
    "ammeter",
    "voltmeter",
    "junction",
]


class CanvasSpec(BaseModel):
    width: int
    height: int


class Point(BaseModel):
    x: float
    y: float


class PortSpec(Point):
    id: str


class SliderRange(BaseModel):
    min_ratio: float = 0.0
    max_ratio: float = 1.0


class ComponentCapabilities(BaseModel):
    editable_value: bool = False
    toggleable: bool = False
    slider_range: Optional[SliderRange] = None
    removable: bool = False


class SceneComponent(BaseModel):
    id: str
    type: SceneComponentType
    label: Optional[str] = None
    x: float
    y: float
    width: float
    height: float
    rotation: float = 0.0
    enabled: bool = True
    value: Optional[float] = None
    display_value: Optional[str] = None
    capabilities: ComponentCapabilities = Field(default_factory=ComponentCapabilities)
    style: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, str] = Field(default_factory=dict)
    ports: List[PortSpec] = Field(default_factory=list)


class WireSegment(BaseModel):
    id: str
    role: str = "main"
    start_ref: str
    end_ref: str
    bends: List[Point] = Field(default_factory=list)


class MeterAnchor(BaseModel):
    component_id: str
    x: float
    y: float


class SceneDocument(BaseModel):
    id: str
    title: str
    canvas: CanvasSpec
    components: List[SceneComponent]
    wires: List[WireSegment]
    meter_anchors: List[MeterAnchor]
    debug: Dict[str, str] = Field(default_factory=dict)
