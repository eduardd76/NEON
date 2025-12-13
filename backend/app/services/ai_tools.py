"""
AI Tool Definitions for Claude
Defines structured tools for topology manipulation
"""

# Tool definitions for Claude API
TOPOLOGY_TOOLS = [
    {
        "name": "add_nodes",
        "description": "Add one or more network devices (routers, switches, firewalls, hosts) to the topology. Use this when the user wants to add devices to their network lab.",
        "input_schema": {
            "type": "object",
            "properties": {
                "nodes": {
                    "type": "array",
                    "description": "List of network devices to add",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Device name (e.g., 'R1', 'Switch1', 'Firewall')"
                            },
                            "type": {
                                "type": "string",
                                "enum": ["router", "switch", "firewall", "host"],
                                "description": "Type of network device"
                            },
                            "image": {
                                "type": "string",
                                "description": "Network OS image name (e.g., 'ceos', 'srlinux', 'frr', 'vios')"
                            },
                            "vendor": {
                                "type": "string",
                                "description": "Vendor name (e.g., 'cisco', 'arista', 'nokia', 'juniper')"
                            },
                            "position": {
                                "type": "object",
                                "description": "Canvas position (optional, will auto-arrange if not provided)",
                                "properties": {
                                    "x": {"type": "integer"},
                                    "y": {"type": "integer"}
                                }
                            }
                        },
                        "required": ["name", "type"]
                    }
                }
            },
            "required": ["nodes"]
        }
    },
    {
        "name": "add_links",
        "description": "Create network connections (links) between devices. Use this when the user wants to connect devices together in the topology.",
        "input_schema": {
            "type": "object",
            "properties": {
                "links": {
                    "type": "array",
                    "description": "List of network links to create",
                    "items": {
                        "type": "object",
                        "properties": {
                            "source": {
                                "type": "string",
                                "description": "Source device name"
                            },
                            "source_interface": {
                                "type": "string",
                                "description": "Source interface (optional, will auto-assign if not provided)"
                            },
                            "target": {
                                "type": "string",
                                "description": "Target device name"
                            },
                            "target_interface": {
                                "type": "string",
                                "description": "Target interface (optional, will auto-assign if not provided)"
                            },
                            "properties": {
                                "type": "object",
                                "description": "Link properties for network impairment (optional)",
                                "properties": {
                                    "bandwidth": {
                                        "type": "string",
                                        "description": "Bandwidth limit (e.g., '1gbit', '100mbit')"
                                    },
                                    "delay_ms": {
                                        "type": "integer",
                                        "description": "Network delay in milliseconds"
                                    },
                                    "loss_percent": {
                                        "type": "number",
                                        "description": "Packet loss percentage (0-100)"
                                    }
                                }
                            }
                        },
                        "required": ["source", "target"]
                    }
                }
            },
            "required": ["links"]
        }
    },
    {
        "name": "create_topology_pattern",
        "description": "Create a complete topology using a predefined pattern (ring, mesh, star, spine-leaf). Use this for common network topologies.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "enum": ["ring", "mesh", "star", "spine-leaf"],
                    "description": "Topology pattern to create"
                },
                "count": {
                    "type": "integer",
                    "description": "Number of devices (for ring, mesh, star) or dict with spines/leaves count"
                },
                "spine_count": {
                    "type": "integer",
                    "description": "Number of spine switches (only for spine-leaf pattern)"
                },
                "leaf_count": {
                    "type": "integer",
                    "description": "Number of leaf switches (only for spine-leaf pattern)"
                },
                "image_type": {
                    "type": "string",
                    "enum": ["router", "switch"],
                    "description": "Type of device to use"
                }
            },
            "required": ["pattern", "image_type"]
        }
    },
    {
        "name": "deploy_lab",
        "description": "Deploy all devices in the current lab. This starts all containers and creates network links. Only use this when the user explicitly asks to deploy or start the lab.",
        "input_schema": {
            "type": "object",
            "properties": {
                "create_links": {
                    "type": "boolean",
                    "description": "Whether to create network links between devices (default: true)",
                    "default": True
                }
            }
        }
    },
    {
        "name": "get_lab_status",
        "description": "Get the current status of the lab including all nodes and links. Use this when the user asks about the current state of their topology.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    }
]


def get_system_prompt(lab_context: str = "", images_context: str = "") -> str:
    """
    Generate system prompt for Claude with tool calling

    Args:
        lab_context: Current lab information
        images_context: Available images information

    Returns:
        System prompt string
    """
    return f"""You are NEON, an AI assistant for building and managing network topologies.

{lab_context}

Available network images:
{images_context}

Your role is to help users create network topologies through natural language. You have access to tools that can:

1. **add_nodes** - Add routers, switches, firewalls, or hosts to the topology
2. **add_links** - Create connections between devices
3. **create_topology_pattern** - Build common patterns (ring, mesh, star, spine-leaf)
4. **deploy_lab** - Start all devices and establish connections
5. **get_lab_status** - Check current topology status

**Guidelines:**

- When users describe a topology, use tools to build it step by step
- For common patterns (ring, mesh, spine-leaf), use create_topology_pattern
- Choose appropriate images based on vendor preferences:
  * Cisco: vios, csr1000v, viosl2
  * Arista: ceos
  * Nokia: srlinux
  * Juniper: vmx, crpd
  * Generic/Free: frr (router), alpine/ubuntu (host)
- Auto-assign interface names unless specifically requested
- Be conversational and explain what you're doing
- Ask for clarification if requirements are unclear
- Don't deploy unless explicitly asked

**Response Format:**

1. Acknowledge the request conversationally
2. Use appropriate tools to execute the action
3. Summarize what was created
4. Suggest next steps if relevant

**Examples:**

User: "Add 3 routers"
→ Use add_nodes with 3 router nodes (R1, R2, R3)
→ Respond: "I've added 3 routers (R1, R2, R3) to your topology. Would you like me to connect them?"

User: "Create a ring of 5 routers"
→ Use create_topology_pattern with pattern="ring", count=5
→ Respond: "I've created a ring topology with 5 routers, each connected to its neighbors."

User: "Connect R1 to R2"
→ Use add_links with source=R1, target=R2
→ Respond: "Connected R1 to R2. The link is ready to be deployed."

User: "Build a spine-leaf datacenter with 2 spines and 4 leaves"
→ Use create_topology_pattern with pattern="spine-leaf", spine_count=2, leaf_count=4
→ Respond: "I've built a spine-leaf topology with 2 spine switches and 4 leaf switches, with full mesh connectivity between spines and leaves."

Be helpful, accurate, and efficient!"""
