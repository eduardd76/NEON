# NEON End-to-End Test Plan
## Comprehensive QA Testing Strategy

---

## Test Environment Setup

### Prerequisites
- Docker Desktop running
- Backend services running (PostgreSQL + FastAPI)
- Frontend development server or production build
- Anthropic API key configured
- Network OS images available

### Test Data
- Test lab name: "QA-Test-Lab"
- Test node names: R1, R2, R3, SW1, SW2
- Test links: R1-R2, R2-R3, R1-SW1

---

## Test Scenarios

### Scenario 1: Application Health Check
**Priority:** Critical
**Description:** Verify all services are running and accessible

**Test Cases:**
1. TC-001: Backend health endpoint responds
   - Endpoint: GET /health
   - Expected: 200 OK, {"status": "healthy"}

2. TC-002: Frontend loads successfully
   - URL: http://localhost:5173 or http://localhost:80
   - Expected: NEON header visible, no console errors

3. TC-003: Database connection works
   - Endpoint: GET /api/v1/images/vendors/
   - Expected: Returns vendor list

4. TC-004: API documentation accessible
   - URL: http://localhost:8000/docs
   - Expected: Swagger UI loads

---

### Scenario 2: Lab Management (UI)
**Priority:** Critical
**Description:** Create and manage labs through the UI

**Test Cases:**
1. TC-010: Create new lab via "New Lab" button
   - Action: Click "New Lab" button
   - Expected: Lab creation modal/form appears

2. TC-011: Lab appears in lab list
   - Expected: Newly created lab visible

3. TC-012: Lab status shows "draft"
   - Expected: Status indicator shows draft

---

### Scenario 3: Node Management (Drag & Drop)
**Priority:** High
**Description:** Add and manage network devices via UI

**Test Cases:**
1. TC-020: Node library loads with images
   - Expected: Sidebar shows categorized devices
   - Expected: Images grouped by type (routers, switches, etc.)

2. TC-021: Drag router from library to canvas
   - Action: Drag cEOS image to canvas
   - Expected: Node appears on canvas at drop position

3. TC-022: Node displays correct information
   - Expected: Node shows label, vendor icon, status indicator

4. TC-023: Multiple nodes can be added
   - Action: Add 3 different nodes
   - Expected: All nodes visible on canvas

5. TC-024: Nodes can be repositioned
   - Action: Drag node to new position
   - Expected: Node moves smoothly

---

### Scenario 4: AI Chat - Simple Node Creation
**Priority:** Critical
**Description:** Test AI topology generation with basic commands

**Test Cases:**
1. TC-030: Chat panel is visible and functional
   - Expected: Chat panel on right side
   - Expected: Input field accepts text

2. TC-031: AI responds to greeting
   - Input: "Hello"
   - Expected: Assistant responds with greeting

3. TC-032: Add single router via AI
   - Input: "Add a router"
   - Expected: Node appears on canvas
   - Expected: Success action indicator in chat

4. TC-033: Add multiple routers via AI
   - Input: "Add 3 Arista routers"
   - Expected: 3 nodes appear on canvas
   - Expected: Action shows "Added 3 nodes: R1, R2, R3"

5. TC-034: Add nodes with vendor specification
   - Input: "Add a Nokia switch"
   - Expected: SR Linux node appears
   - Expected: Correct vendor image used

---

### Scenario 5: AI Chat - Topology Patterns
**Priority:** High
**Description:** Test complex topology generation

**Test Cases:**
1. TC-040: Create ring topology
   - Input: "Create a ring topology with 5 routers"
   - Expected: 5 nodes appear in positions
   - Expected: 5 links created (ring pattern)
   - Expected: Success message with node/link count

2. TC-041: Create mesh topology
   - Input: "Build a mesh network with 4 devices"
   - Expected: 4 nodes with full mesh links
   - Expected: 6 links total (n*(n-1)/2)

3. TC-042: Create spine-leaf topology
   - Input: "Make a spine-leaf datacenter with 2 spines and 4 leaves"
   - Expected: 2 spine nodes + 4 leaf nodes
   - Expected: 8 links (each leaf to each spine)

4. TC-043: Create star topology
   - Input: "Create a star topology with 5 devices"
   - Expected: 1 core node + 4 edge nodes
   - Expected: 4 links (core to each edge)

---

### Scenario 6: Manual Link Creation
**Priority:** High
**Description:** Create links manually between nodes

**Test Cases:**
1. TC-050: Connect two nodes via canvas
   - Action: Drag from node1 handle to node2 handle
   - Expected: Link appears between nodes
   - Expected: Link added to database

2. TC-051: Connect nodes via AI chat
   - Input: "Connect R1 to R2"
   - Expected: Link created with auto-assigned interfaces
   - Expected: Action shows "Created 1 link"

3. TC-052: Link shows connection endpoints
   - Expected: Link displays source/target info on hover
   - Expected: Interface names visible

---

### Scenario 7: Node Properties Panel
**Priority:** High
**Description:** Test node selection and properties

**Test Cases:**
1. TC-060: Click node to select
   - Action: Click on a node
   - Expected: Properties panel appears on right

2. TC-061: Properties panel shows node details
   - Expected: Node name, type, vendor visible
   - Expected: Resource allocation (CPU, memory) shown
   - Expected: Status indicator visible

3. TC-062: Console button disabled for stopped nodes
   - Expected: "Open Console" button disabled
   - Expected: Start button enabled

4. TC-063: Start node via properties panel
   - Action: Click "Start" button
   - Expected: Node status changes to "starting"
   - Expected: After delay, status becomes "running"

5. TC-064: Delete node via properties panel
   - Action: Click "Delete" button
   - Confirm: Click confirmation
   - Expected: Node removed from canvas
   - Expected: Node removed from database

---

### Scenario 8: Console Access
**Priority:** High
**Description:** Test WebSocket console functionality

**Test Cases:**
1. TC-070: Open console for running node
   - Prerequisite: Node status = "running"
   - Action: Click "Open Console" button
   - Expected: Console window appears
   - Expected: Terminal shows connection message

2. TC-071: Console receives output
   - Expected: Terminal displays container shell prompt

3. TC-072: Console accepts input
   - Action: Type command and press Enter
   - Expected: Command executes in container

4. TC-073: Console can be maximized
   - Action: Click maximize button
   - Expected: Console expands to full screen

5. TC-074: Console can be closed
   - Action: Click close button
   - Expected: Console window closes
   - Expected: WebSocket connection terminated

---

### Scenario 9: Lab Deployment
**Priority:** Critical
**Description:** Deploy complete lab topology

**Test Cases:**
1. TC-080: Deploy lab via AI chat
   - Setup: Lab with 3 nodes and 2 links
   - Input: "Deploy the lab"
   - Expected: All nodes start (status → "starting" → "running")
   - Expected: All links created (status → "up")
   - Expected: Action shows deployment progress

2. TC-081: Nodes receive management IPs
   - Expected: Each node has mgmt_ip assigned
   - Expected: IP visible in properties panel

3. TC-082: Links are established
   - Expected: veth pairs created
   - Expected: Interfaces configured

4. TC-083: Lab status updates
   - Expected: Lab status changes to "running"

---

### Scenario 10: Lab Status Query
**Priority:** Medium
**Description:** Query lab information via AI

**Test Cases:**
1. TC-090: Get lab status via AI
   - Input: "Show me the lab status"
   - Expected: Response lists all nodes
   - Expected: Response lists all links
   - Expected: Status for each component shown

---

### Scenario 11: Error Handling
**Priority:** High
**Description:** Test error scenarios and edge cases

**Test Cases:**
1. TC-100: AI chat without API key
   - Setup: Remove ANTHROPIC_API_KEY
   - Input: "Add a router"
   - Expected: Error message displayed
   - Expected: Helpful guidance provided

2. TC-101: Invalid topology request
   - Input: "Create a topology with -5 nodes"
   - Expected: Error message or clarification request

3. TC-102: Deploy without nodes
   - Input: "Deploy the lab" (empty lab)
   - Expected: Error or warning message

4. TC-103: Connect non-existent nodes
   - Input: "Connect R99 to R100"
   - Expected: Error message: "Node not found"

5. TC-104: Console access for non-deployed node
   - Action: Try to open console for stopped node
   - Expected: Console button disabled
   - Expected: Tooltip explains why

6. TC-105: Duplicate node names
   - Input: "Add router named R1" (twice)
   - Expected: Second node gets unique name (R1-1 or error)

---

### Scenario 12: Multi-Vendor Support
**Priority:** Medium
**Description:** Test different network OS images

**Test Cases:**
1. TC-110: Add Arista cEOS node
   - Input: "Add an Arista router"
   - Expected: cEOS image used

2. TC-111: Add Nokia SR Linux node
   - Input: "Add a Nokia switch"
   - Expected: srlinux image used

3. TC-112: Add Cisco IOS node
   - Input: "Add a Cisco router"
   - Expected: vios or csr1000v image used

4. TC-113: Add FRR node
   - Input: "Add a FRR router"
   - Expected: frr image used

5. TC-114: Add Linux host
   - Input: "Add an Ubuntu host"
   - Expected: ubuntu image used

---

### Scenario 13: UI Responsiveness
**Priority:** Medium
**Description:** Test UI behavior and performance

**Test Cases:**
1. TC-120: Canvas zoom and pan
   - Action: Use mouse wheel to zoom
   - Expected: Canvas zooms smoothly

2. TC-121: Minimap navigation
   - Action: Click minimap
   - Expected: Canvas pans to clicked area

3. TC-122: Chat scrolls with messages
   - Action: Send 20+ messages
   - Expected: Chat auto-scrolls to bottom

4. TC-123: Loading states display
   - Expected: Loading indicator shown during AI calls
   - Expected: Buttons disabled during loading

5. TC-124: Multiple panels work together
   - Expected: NodeLibrary + Canvas + NodePanel + ChatPanel all visible
   - Expected: No overlap or layout issues

---

### Scenario 14: Data Persistence
**Priority:** High
**Description:** Test data saves correctly

**Test Cases:**
1. TC-130: Created nodes persist in database
   - Action: Create nodes via AI
   - Verify: Query /api/v1/labs/{id}
   - Expected: Nodes in response

2. TC-131: Links persist in database
   - Action: Create links
   - Verify: Links in API response

3. TC-132: Node positions save
   - Action: Move node
   - Refresh page
   - Expected: Node at new position

4. TC-133: Lab status persists
   - Action: Deploy lab
   - Verify: Lab status = "running" in database

---

### Scenario 15: Clean Up
**Priority:** Medium
**Description:** Test resource cleanup

**Test Cases:**
1. TC-140: Stop node cleans up container
   - Action: Stop running node
   - Expected: Container stopped
   - Expected: Node status = "stopped"

2. TC-141: Delete node removes container
   - Action: Delete deployed node
   - Expected: Container removed
   - Expected: Node removed from database

3. TC-142: Delete lab cleans up all resources
   - Action: Delete lab
   - Expected: All nodes removed
   - Expected: All links removed
   - Expected: All containers removed

---

## Test Execution Checklist

### Pre-Test
- [ ] Services running: `docker-compose ps`
- [ ] Database seeded: Vendors and images present
- [ ] Frontend accessible: Browser opens without errors
- [ ] API accessible: Swagger UI loads

### During Test
- [ ] Record screenshots for each scenario
- [ ] Note any console errors
- [ ] Track response times
- [ ] Document unexpected behavior

### Post-Test
- [ ] All containers stopped
- [ ] Database cleaned (if needed)
- [ ] Test results documented
- [ ] Issues logged with screenshots

---

## Success Criteria

### Critical (Must Pass)
- ✓ Application loads without errors
- ✓ AI chat responds to basic commands
- ✓ Nodes can be added via AI
- ✓ Topology patterns work correctly
- ✓ Lab deployment succeeds
- ✓ Console access functional

### High Priority (Should Pass)
- ✓ Manual link creation works
- ✓ Properties panel displays correctly
- ✓ Multi-vendor images supported
- ✓ Error messages are helpful
- ✓ Data persists correctly

### Medium Priority (Nice to Have)
- ✓ UI is responsive
- ✓ All vendors work
- ✓ Performance is acceptable
- ✓ Cleanup works properly

---

## Test Report Template

```markdown
# NEON E2E Test Report
**Date:** YYYY-MM-DD
**Tester:** QA Engineer
**Version:** v2.5.0
**Environment:** Local Docker

## Summary
- Total Test Cases: XX
- Passed: XX
- Failed: XX
- Blocked: XX
- Pass Rate: XX%

## Critical Issues
1. [Issue description]
   - Severity: Critical/High/Medium/Low
   - Steps to reproduce
   - Expected vs Actual
   - Screenshot

## Recommendations
- [List of improvements]

## Sign-off
- [ ] All critical tests passed
- [ ] All blocking issues resolved
- [ ] Ready for deployment
```

---

**Status:** 📋 READY FOR EXECUTION
**Next:** Execute tests with Playwright
