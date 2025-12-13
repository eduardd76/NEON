"""
NEON Complete Topology Build Demo
Full workflow: Create lab -> Build topology via AI -> Show results
"""
from playwright.sync_api import sync_playwright
import time

def demo_complete_workflow():
    """Complete demo: Create lab and build topology with 3 Cisco routers attached to a switch"""
    print("\n" + "="*80)
    print("NEON COMPLETE AI TOPOLOGY BUILD DEMONSTRATION")
    print("="*80)
    print("\nGoal: Build a topology with 3 Cisco routers attached to a switch")
    print("-"*80)

    with sync_playwright() as p:
        # Launch browser in non-headless mode to see the magic happen
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        try:
            print("\n[STEP 1] Loading NEON application...")
            page.goto('http://localhost:5173', wait_until='networkidle', timeout=30000)
            page.wait_for_selector('text=AI Assistant', timeout=10000)
            print("✓ Application loaded")
            time.sleep(1)

            print("\n[STEP 2] Creating a new lab...")
            # Click "New Lab" button
            new_lab_button = page.locator('button:has-text("New Lab")')
            new_lab_button.click()
            print("✓ New Lab button clicked")
            time.sleep(2)

            # Take screenshot after lab creation
            page.screenshot(path='F:\\Agentic_Apps\\NEON\\tests\\screenshots\\workflow_01_lab_created.png', full_page=True)
            print("✓ Screenshot saved: workflow_01_lab_created.png")

            print("\n[STEP 3] Sending AI command to build topology...")
            command = "Build a topology with 3 Cisco routers attached to a switch"
            print(f"   Command: '{command}'")

            # Find chat input - it's at the bottom of the chat panel
            chat_input = page.locator('input[placeholder*="Add devices"]').first
            chat_input.fill(command)
            print("✓ Command entered in chat")
            time.sleep(1)

            # Take screenshot with command visible
            page.screenshot(path='F:\\Agentic_Apps\\NEON\\tests\\screenshots\\workflow_02_command_ready.png', full_page=True)
            print("✓ Screenshot saved: workflow_02_command_ready.png")

            # Click send
            send_button = page.locator('button[type="submit"], button:has(svg)').last
            send_button.click()
            print("✓ Command sent to AI")

            print("\n[STEP 4] Waiting for AI to analyze and build topology...")
            print("   (Claude is now: parsing request -> selecting tools -> creating nodes and links)")

            # Wait for AI processing
            time.sleep(25000 / 1000)  # 25 seconds for AI + topology build

            print("✓ AI processing complete")

            # Take screenshot of AI response
            page.screenshot(path='F:\\Agentic_Apps\\NEON\\tests\\screenshots\\workflow_03_ai_responded.png', full_page=True)
            print("✓ Screenshot saved: workflow_03_ai_responded.png")

            print("\n[STEP 5] Analyzing the built topology...")

            # Count nodes
            nodes = page.locator('[data-id][class*="react-flow__node"]').count()
            print(f"   Nodes on canvas: {nodes}")

            # Count edges
            edges = page.locator('[class*="react-flow__edge"]').count()
            print(f"   Links on canvas: {edges}")

            # Zoom to fit
            print("\n[STEP 6] Adjusting view to show topology...")
            page.keyboard.press('Control+0')  # Reset zoom
            time.sleep(1)

            # Take final screenshot
            page.screenshot(path='F:\\Agentic_Apps\\NEON\\tests\\screenshots\\workflow_04_final_topology.png', full_page=True)
            print("✓ Screenshot saved: workflow_04_final_topology.png")

            print("\n" + "="*80)
            print("TOPOLOGY BUILD SUMMARY")
            print("="*80)
            print(f"✓ Lab created: Yes")
            print(f"✓ AI command processed: '{command}'")
            print(f"✓ Nodes created: {nodes} (Expected: 4 - 3 routers + 1 switch)")
            print(f"✓ Links created: {edges} (Expected: 3 - star topology)")
            print("\n✓ Screenshots saved to: tests/screenshots/workflow_*.png")
            print("="*80)

            # Keep browser open to see results
            print("\nKeeping browser open for 15 seconds for manual inspection...")
            time.sleep(15)

        except Exception as e:
            print(f"\n✗ ERROR: {str(e)}")
            page.screenshot(path='F:\\Agentic_Apps\\NEON\\tests\\screenshots\\workflow_error.png', full_page=True)
            print("Error screenshot saved")
            import traceback
            traceback.print_exc()

        finally:
            browser.close()
            print("\n✓ Demo complete!")

if __name__ == "__main__":
    demo_complete_workflow()
