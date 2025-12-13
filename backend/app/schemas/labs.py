"""
Pydantic schemas for Labs API
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from uuid import UUID
from datetime import datetime


class LabBase(BaseModel):
    name: str
    description: Optional[str] = None


class LabCreate(LabBase):
    pass


class LabUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class ImageSummary(BaseModel):
    id: UUID
    name: str
    display_name: str
    type: str


class NodePosition(BaseModel):
    x: int
    y: int


class NodeResources(BaseModel):
    cpu: Optional[int] = None
    memory: Optional[int] = None


class NodeBase(BaseModel):
    name: str
    hostname: Optional[str] = None
    position_x: int = 100
    position_y: int = 100
    cpu: Optional[int] = None
    memory: Optional[int] = None


class NodeCreate(NodeBase):
    image_id: UUID


class NodeResponse(BaseModel):
    id: UUID
    name: str
    hostname: Optional[str] = None
    image: Optional[ImageSummary] = None
    position: NodePosition
    resources: NodeResources
    status: str
    mgmt_ip: Optional[str] = None
    console_port: Optional[int] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            name=obj.name,
            hostname=obj.hostname,
            image=ImageSummary(
                id=obj.image.id,
                name=obj.image.name,
                display_name=obj.image.display_name,
                type=obj.image.type
            ) if obj.image else None,
            position=NodePosition(x=obj.position_x, y=obj.position_y),
            resources=NodeResources(cpu=obj.cpu, memory=obj.memory),
            status=obj.status,
            mgmt_ip=str(obj.mgmt_ip) if obj.mgmt_ip else None,
            console_port=obj.console_port
        )


class LinkEndpoint(BaseModel):
    node_id: UUID
    interface: str


class LinkProperties(BaseModel):
    bandwidth: Optional[str] = None
    delay_ms: Optional[int] = 0
    loss_percent: Optional[float] = 0.0
    jitter_ms: Optional[int] = 0


class LinkBase(BaseModel):
    source_node_id: UUID
    source_interface: str
    target_node_id: UUID
    target_interface: str


class LinkCreate(LinkBase):
    pass


class LinkResponse(BaseModel):
    id: UUID
    source: LinkEndpoint
    target: LinkEndpoint
    properties: LinkProperties
    status: str

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            source=LinkEndpoint(node_id=obj.source_node_id, interface=obj.source_interface),
            target=LinkEndpoint(node_id=obj.target_node_id, interface=obj.target_interface),
            properties=LinkProperties(
                bandwidth=obj.bandwidth,
                delay_ms=obj.delay_ms,
                loss_percent=float(obj.loss_percent) if obj.loss_percent else 0.0,
                jitter_ms=obj.jitter_ms
            ),
            status=obj.status
        )


class LabResponse(LabBase):
    id: UUID
    status: str
    nodes: List[NodeResponse] = []
    links: List[LinkResponse] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deployed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LabSummary(LabBase):
    id: UUID
    status: str
    node_count: int
    link_count: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deployed_at: Optional[datetime] = None


class LabListResponse(BaseModel):
    count: int
    labs: List[LabSummary]


class DeployResult(BaseModel):
    message: str
    status: str
    nodes: List[Dict] = []
    links: List[Dict] = []
