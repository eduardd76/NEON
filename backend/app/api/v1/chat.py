"""
Chat API endpoint for AI-powered natural language interface
Uses Claude API to interpret user requests and generate topology actions
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Optional
from uuid import UUID
import logging

from app.db.base import get_db
from app.db.models import Lab, Image
from app.core.config import settings

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


class ChatResponse(BaseModel):
    response: str
    actions: Optional[List[Dict]] = None
    suggestions: Optional[List[str]] = None


@router.post("/", response_model=ChatResponse)
async def chat(
    message: ChatMessage,
    db: Session = Depends(get_db)
):
    """
    Process natural language requests for topology building

    Examples:
    - "Add 3 routers with OSPF"
    - "Create a spine-leaf topology with 2 spines and 4 leaves"
    - "Connect R1 to R2"
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

        # Get lab context if lab_id is provided
        lab_context = ""
        if message.lab_id:
            lab = db.query(Lab).filter(Lab.id == message.lab_id).first()
            if lab:
                lab_context = f"""
Current lab: {lab.name}
Status: {lab.status}
Nodes: {len(lab.nodes)}
Links: {len(lab.links)}
"""

        # Get available images
        images = db.query(Image).filter(Image.is_active == True).all()
        images_context = "\n".join([
            f"- {img.display_name} ({img.type}, {img.runtime})"
            for img in images[:10]  # Limit to prevent token overflow
        ])

        # Create system prompt
        system_prompt = f"""You are NEON, an AI assistant for network topology building and emulation.

{lab_context}

Available network images:
{images_context}

Your role is to help users:
1. Create network topologies using natural language
2. Add/remove network devices (routers, switches, firewalls, hosts)
3. Connect devices together
4. Configure routing protocols
5. Deploy and manage labs

When the user requests topology changes, provide:
1. A friendly response explaining what you'll do
2. Actions array with structured commands
3. Suggestions for next steps

Action format:
{{
  "type": "add_node" | "add_link" | "deploy" | "configure",
  "params": {{relevant parameters}}
}}

Keep responses concise and actionable."""

        # Call Claude API
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": message.message
            }]
        )

        # Parse response
        assistant_message = response.content[0].text

        # For MVP, return text response
        # Full implementation would parse actions from structured output
        return ChatResponse(
            response=assistant_message,
            actions=[],
            suggestions=[
                "Add more devices",
                "Connect devices",
                "Deploy lab",
                "Configure protocols"
            ]
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@router.get("/suggestions")
async def get_suggestions(db: Session = Depends(get_db)):
    """Get quick action suggestions for users"""

    suggestions = [
        "Add a router to the topology",
        "Create a simple 3-router mesh",
        "Add a spine-leaf topology",
        "Connect all routers in a ring",
        "Deploy the current lab",
        "Show me datacenter images",
        "Create a MPLS backbone"
    ]

    return {"suggestions": suggestions}
