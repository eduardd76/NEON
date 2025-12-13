# Phase 5 (v2.5) Implementation Plan
## Enhanced AI Topology Generation + Batfish Validation

---

## 🎯 Objectives

1. **AI-Powered Topology Building**
   - Use Claude's tool calling for structured topology actions
   - Generate complete topologies from natural language
   - Support complex scenarios (spine-leaf, ring, mesh, etc.)

2. **Configuration Management**
   - Device configuration templates (OSPF, BGP, interfaces)
   - Vendor-specific templates (Cisco, Arista, Juniper, Nokia)
   - Automated configuration generation

3. **Network Validation**
   - Batfish integration for pre-deployment validation
   - Routing table analysis
   - ACL conflict detection
   - Reachability verification

4. **Enhanced Chat Experience**
   - Preview AI-generated actions before execution
   - User approval workflow
   - Real-time progress updates
   - Error handling and rollback

---

## 📋 Technical Design

### 1. AI Tool Calling Schema

Define Claude tools for topology manipulation:

```python
tools = [
    {
        "name": "add_nodes",
        "description": "Add one or more network devices to the topology",
        "input_schema": {
            "type": "object",
            "properties": {
                "nodes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string", "enum": ["router", "switch", "firewall", "host"]},
                            "image": {"type": "string"},
                            "position": {"type": "object"}
                        }
                    }
                }
            }
        }
    },
    {
        "name": "add_links",
        "description": "Create network connections between devices",
        "input_schema": {
            "type": "object",
            "properties": {
                "links": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "source": {"type": "string"},
                            "source_interface": {"type": "string"},
                            "target": {"type": "string"},
                            "target_interface": {"type": "string"},
                            "properties": {"type": "object"}
                        }
                    }
                }
            }
        }
    },
    {
        "name": "configure_device",
        "description": "Generate configuration for a network device",
        "input_schema": {
            "type": "object",
            "properties": {
                "device": {"type": "string"},
                "config_type": {"type": "string", "enum": ["ospf", "bgp", "interfaces", "base"]},
                "parameters": {"type": "object"}
            }
        }
    },
    {
        "name": "deploy_topology",
        "description": "Deploy all devices in the current topology",
        "input_schema": {
            "type": "object",
            "properties": {
                "validate": {"type": "boolean", "default": True}
            }
        }
    }
]
```

### 2. Topology Builder Service

```python
# backend/app/services/topology_builder.py

class TopologyBuilder:
    """Builds topologies from AI-generated actions"""

    def add_nodes(self, lab_id: UUID, nodes: List[Dict], db: Session) -> List[Node]
    def add_links(self, lab_id: UUID, links: List[Dict], db: Session) -> List[Link]
    def configure_device(self, node_id: UUID, config_type: str, params: Dict, db: Session) -> str
    def deploy_topology(self, lab_id: UUID, validate: bool, db: Session) -> DeployResult

    # Helper methods
    def _calculate_positions(self, topology_type: str, count: int) -> List[Position]
    def _auto_assign_interfaces(self, node_a: Node, node_b: Node) -> Tuple[str, str]
    def _validate_topology(self, lab: Lab) -> ValidationResult
```

### 3. Configuration Templates

```python
# backend/app/templates/configs/

cisco_ospf.j2
arista_ospf.j2
juniper_ospf.j2
nokia_ospf.j2

cisco_bgp.j2
arista_bgp.j2

cisco_interfaces.j2
arista_interfaces.j2
```

Example template (cisco_ospf.j2):
```jinja2
!
hostname {{ hostname }}
!
router ospf {{ process_id }}
  router-id {{ router_id }}
  {% for network in networks %}
  network {{ network.address }} {{ network.wildcard }} area {{ network.area }}
  {% endfor %}
!
{% for interface in interfaces %}
interface {{ interface.name }}
  ip address {{ interface.ip }} {{ interface.mask }}
  ip ospf {{ process_id }} area {{ interface.area }}
  no shutdown
!
{% endfor %}
```

### 4. Batfish Integration

```python
# backend/app/services/batfish_validator.py

from pybatfish.client.session import Session
from pybatfish.datamodel import *

class BatfishValidator:
    """Network validation using Batfish"""

    def __init__(self):
        self.session = Session(host="localhost")

    def validate_topology(self, lab: Lab) -> ValidationResult:
        """Run comprehensive topology validation"""

        # Initialize Batfish network
        network_name = f"neon-lab-{lab.id}"
        snapshot_name = "current"

        # Convert NEON topology to Batfish format
        configs = self._export_configs(lab)

        # Load snapshot
        self.session.init_snapshot(configs, name=snapshot_name, network=network_name)

        results = {
            "routing": self._validate_routing(),
            "reachability": self._validate_reachability(),
            "acls": self._validate_acls(),
            "interfaces": self._validate_interfaces()
        }

        return ValidationResult(**results)

    def _validate_routing(self) -> RoutingValidation
    def _validate_reachability(self) -> ReachabilityValidation
    def _validate_acls(self) -> ACLValidation
    def _validate_interfaces(self) -> InterfaceValidation
```

### 5. Enhanced Chat API

```python
# backend/app/api/v1/chat.py

@router.post("/", response_model=ChatResponse)
async def chat_with_tools(message: ChatMessage, db: Session = Depends(get_db)):
    """
    Enhanced chat with tool calling support
    """

    # Call Claude with tools
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        tools=TOPOLOGY_TOOLS,
        messages=[{"role": "user", "content": message.message}]
    )

    actions = []

    # Process tool calls
    for content_block in response.content:
        if content_block.type == "tool_use":
            action = await execute_tool_call(
                tool_name=content_block.name,
                tool_input=content_block.input,
                lab_id=message.lab_id,
                db=db
            )
            actions.append(action)

    return ChatResponse(
        response=extract_text(response),
        actions=actions,
        preview=True  # Requires user approval
    )

async def execute_tool_call(tool_name: str, tool_input: Dict, lab_id: UUID, db: Session):
    """Execute AI-generated tool call"""

    builder = TopologyBuilder()

    if tool_name == "add_nodes":
        return builder.add_nodes(lab_id, tool_input["nodes"], db)

    elif tool_name == "add_links":
        return builder.add_links(lab_id, tool_input["links"], db)

    elif tool_name == "configure_device":
        return builder.configure_device(
            tool_input["device"],
            tool_input["config_type"],
            tool_input["parameters"],
            db
        )

    elif tool_name == "deploy_topology":
        return builder.deploy_topology(lab_id, tool_input.get("validate", True), db)
```

### 6. Frontend Action Preview

```tsx
// frontend/src/components/chat/ActionPreview.tsx

interface ActionPreviewProps {
  actions: TopologyAction[];
  onApprove: () => void;
  onReject: () => void;
}

export function ActionPreview({ actions, onApprove, onReject }: ActionPreviewProps) {
  return (
    <div className="border rounded-lg p-4 bg-blue-50">
      <h4 className="font-semibold mb-2">Preview Actions</h4>

      <div className="space-y-2">
        {actions.map((action, idx) => (
          <ActionCard key={idx} action={action} />
        ))}
      </div>

      <div className="flex gap-2 mt-4">
        <Button onClick={onApprove} variant="default">
          ✓ Apply Changes
        </Button>
        <Button onClick={onReject} variant="outline">
          ✗ Cancel
        </Button>
      </div>
    </div>
  );
}
```

---

## 📦 Dependencies

### Backend
```txt
# Add to requirements.txt
pybatfish==2024.1.11.0     # Network validation
jinja2==3.1.3               # Configuration templates
```

### Frontend
No new dependencies required

---

## 🔄 Implementation Order

### Step 1: AI Tool Calling (Priority 1)
- [ ] Define tool schemas
- [ ] Update chat API to use tools
- [ ] Create TopologyBuilder service
- [ ] Test with simple examples ("Add 3 routers")

### Step 2: Configuration Templates (Priority 2)
- [ ] Create template directory structure
- [ ] Implement OSPF templates (Cisco, Arista)
- [ ] Implement BGP templates
- [ ] Add interface configuration templates
- [ ] Template rendering service

### Step 3: Action Preview UI (Priority 3)
- [ ] Create ActionPreview component
- [ ] Update ChatPanel to show previews
- [ ] Implement approve/reject workflow
- [ ] Add real-time execution progress

### Step 4: Batfish Integration (Priority 4)
- [ ] Install Batfish (Docker container)
- [ ] Create BatfishValidator service
- [ ] Export topology to Batfish format
- [ ] Implement validation checks
- [ ] Display validation results in UI

---

## 🧪 Testing Strategy

### Unit Tests
- Tool schema validation
- Template rendering
- TopologyBuilder methods
- Batfish API integration

### Integration Tests
1. **Simple Topology**: "Add 3 routers connected in a ring"
2. **Spine-Leaf**: "Create a spine-leaf topology with 2 spines and 4 leaves"
3. **Configuration**: "Configure OSPF on all routers in area 0"
4. **Deployment**: "Deploy the topology and validate with Batfish"

### Manual Testing
- Chat with various topology requests
- Preview and approve actions
- Verify deployed configurations
- Check Batfish validation results

---

## 📊 Success Criteria

✅ AI can generate complete topologies from natural language
✅ Tool calling executes structured topology actions
✅ Configuration templates support major vendors
✅ Batfish validates topologies before deployment
✅ UI shows action previews and requires approval
✅ End-to-end: "Create datacenter topology" → deployed and validated

---

## 🚀 Timeline Estimate

- **Tool Calling**: 2-3 hours
- **TopologyBuilder**: 2-3 hours
- **Templates**: 1-2 hours
- **UI Preview**: 1-2 hours
- **Batfish** (optional for v2.5): 3-4 hours
- **Testing**: 2-3 hours

**Total**: 8-12 hours (excluding Batfish: 5-8 hours)

---

## 💡 For v2.5 MVP

**Include:**
- ✅ AI tool calling for topology generation
- ✅ TopologyBuilder service
- ✅ Basic configuration templates
- ✅ Action preview in chat UI

**Defer to v3.0:**
- ❌ Batfish integration (complex setup)
- ❌ Advanced validation
- ❌ Configuration rollback

This keeps v2.5 focused and achievable!

---

**Status**: 📋 PLANNED - Ready for implementation
**Next**: Begin with AI tool calling implementation
