"""
Enhanced Chat API with AI Tool Calling
Uses Claude API with structured tools for topology manipulation
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from uuid import UUID
import logging

from app.db.base import get_db
from app.db.models import Lab, Image, Node
from app.core.config import settings
from app.services.topology_builder import TopologyBuilder
from app.services.ai_tools import TOPOLOGY_TOOLS, get_system_prompt
from app.runtime.manager import get_runtime

# Import Anthropic client
try:
    from anthropic import Anthropic
    anthropic_available = True
except ImportError:
    anthropic_available = False

logger = logging.getLogger(__name__)
router = APIRouter()


class ChatMessage(BaseModel):
    message: str
    lab_id: Optional[UUID] = None
    context: Optional[Dict] = None


class ChatAction(BaseModel):
    type: str
    description: str
    data: Dict
    status: str = "pending"  # pending, success, error


class ChatResponse(BaseModel):
    response: str
    actions: List[ChatAction] = []
    suggestions: Optional[List[str]] = None
    preview: bool = False  # Requires user approval


@router.post("/", response_model=ChatResponse)
async def chat_with_tools(
    message: ChatMessage,
    db: Session = Depends(get_db)
):
    """
    Process natural language requests using Claude's tool calling

    Examples:
    - "Add 3 Arista routers"
    - "Create a ring topology with 5 routers"
    - "Connect R1 to R2"
    - "Build a spine-leaf datacenter with 2 spines and 4 leaves"
    - "Deploy the lab"
    """

    # Check if Anthropic API key is configured
    if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY == "":
        return ChatResponse(
            response="AI assistant is not configured. Please add ANTHROPIC_API_KEY to environment variables.",
            actions=[],
            suggestions=[]
        )

    if not anthropic_available:
        return ChatResponse(
            response="Anthropic library not installed. Run: pip install anthropic",
            actions=[],
            suggestions=[]
        )

    try:
        # Initialize Claude client
        client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        # Get lab context
        lab = None
        lab_context = ""
        if message.lab_id:
            lab = db.query(Lab).filter(Lab.id == message.lab_id).first()
            if lab:
                lab_context = f"""Current Lab: {lab.name}
Status: {lab.status}
Nodes: {len(lab.nodes)} ({', '.join([n.name for n in lab.nodes[:10]])})
Links: {len(lab.links)}"""

        # Get available images
        images = db.query(Image).filter(Image.is_active == True).all()
        images_context = "\n".join([
            f"- {img.display_name} ({img.type}, vendor: {img.vendor.name})"
            for img in images[:15]  # Limit to prevent token overflow
        ])

        # Create system prompt
        system_prompt = get_system_prompt(lab_context, images_context)

        # Call Claude API with tools
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=system_prompt,
            tools=TOPOLOGY_TOOLS,
            messages=[{
                "role": "user",
                "content": message.message
            }]
        )

        # Process response
        actions = []
        text_response = ""

        for content_block in response.content:
            if content_block.type == "text":
                text_response += content_block.text

            elif content_block.type == "tool_use":
                # Execute tool call
                action = await execute_tool_call(
                    tool_name=content_block.name,
                    tool_input=content_block.input,
                    lab_id=message.lab_id,
                    db=db
                )
                actions.append(action)

        # Generate suggestions
        suggestions = [
            "Add more devices",
            "Connect devices",
            "Create a topology pattern",
            "Deploy the lab"
        ]

        return ChatResponse(
            response=text_response or "Actions executed successfully!",
            actions=actions,
            suggestions=suggestions,
            preview=False  # Actions already executed
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


async def execute_tool_call(
    tool_name: str,
    tool_input: Dict[str, Any],
    lab_id: Optional[UUID],
    db: Session
) -> ChatAction:
    """
    Execute an AI-generated tool call

    Args:
        tool_name: Name of the tool to execute
        tool_input: Tool input parameters
        lab_id: Current lab ID
        db: Database session

    Returns:
        ChatAction with execution result
    """
    try:
        builder = TopologyBuilder()

        if tool_name == "add_nodes":
            result = builder.add_nodes(lab_id, tool_input["nodes"], db)
            return ChatAction(
                type="add_nodes",
                description=f"Added {len(result)} nodes: {', '.join([n['name'] for n in result])}",
                data={"nodes": result},
                status="success"
            )

        elif tool_name == "add_links":
            result = builder.add_links(lab_id, tool_input["links"], db)
            return ChatAction(
                type="add_links",
                description=f"Created {len(result)} links",
                data={"links": result},
                status="success"
            )

        elif tool_name == "create_topology_pattern":
            pattern = tool_input["pattern"]

            if pattern == "spine-leaf":
                count = {
                    "spines": tool_input.get("spine_count", 2),
                    "leaves": tool_input.get("leaf_count", 4)
                }
            else:
                count = tool_input.get("count", 3)

            result = builder.create_topology_pattern(
                lab_id=lab_id,
                pattern=pattern,
                count=count,
                image_type=tool_input.get("image_type", "router"),
                db=db
            )

            return ChatAction(
                type="create_topology_pattern",
                description=f"Created {pattern} topology with {len(result['nodes'])} nodes and {len(result['links'])} links",
                data=result,
                status="success"
            )

        elif tool_name == "deploy_lab":
            # Get lab
            lab = db.query(Lab).filter(Lab.id == lab_id).first()
            if not lab:
                raise ValueError("Lab not found")

            runtime = get_runtime()
            deployed_nodes = []
            created_links = []

            # Deploy each node
            for node in lab.nodes:
                if node.status == "stopped":
                    result = await runtime.deploy_node(node, node.image, db)
                    deployed_nodes.append({
                        "name": node.name,
                        "container_id": result.get("container_id")
                    })

            # Create links if requested
            if tool_input.get("create_links", True):
                for link in lab.links:
                    if link.status == "down":
                        result = await runtime.create_link(link, db)
                        if result.get("status") == "created":
                            created_links.append({
                                "source": f"{link.source_node.name}:{link.source_interface}",
                                "target": f"{link.target_node.name}:{link.target_interface}"
                            })

            lab.status = "running"
            db.commit()

            return ChatAction(
                type="deploy_lab",
                description=f"Deployed {len(deployed_nodes)} nodes and created {len(created_links)} links",
                data={
                    "nodes": deployed_nodes,
                    "links": created_links
                },
                status="success"
            )

        elif tool_name == "get_lab_status":
            lab = db.query(Lab).filter(Lab.id == lab_id).first()
            if not lab:
                raise ValueError("Lab not found")

            nodes_status = [
                {
                    "name": node.name,
                    "type": node.image.type,
                    "status": node.status,
                    "mgmt_ip": str(node.mgmt_ip) if node.mgmt_ip else None
                }
                for node in lab.nodes
            ]

            links_status = [
                {
                    "source": f"{link.source_node.name}:{link.source_interface}",
                    "target": f"{link.target_node.name}:{link.target_interface}",
                    "status": link.status
                }
                for link in lab.links
            ]

            return ChatAction(
                type="get_lab_status",
                description=f"Lab '{lab.name}' has {len(nodes_status)} nodes and {len(links_status)} links",
                data={
                    "lab": {
                        "name": lab.name,
                        "status": lab.status
                    },
                    "nodes": nodes_status,
                    "links": links_status
                },
                status="success"
            )

        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    except Exception as e:
        logger.error(f"Tool execution error ({tool_name}): {e}")
        return ChatAction(
            type=tool_name,
            description=f"Error: {str(e)}",
            data={"error": str(e)},
            status="error"
        )


@router.get("/suggestions")
async def get_suggestions(db: Session = Depends(get_db)):
    """Get quick action suggestions for users"""

    suggestions = [
        "Add 3 Arista routers",
        "Create a ring of 5 routers",
        "Build a spine-leaf datacenter with 2 spines and 4 leaves",
        "Connect all routers in a mesh",
        "Deploy the current lab",
        "Show me the lab status",
        "Add a Cisco router and connect it to R1"
    ]

    return {"suggestions": suggestions}
