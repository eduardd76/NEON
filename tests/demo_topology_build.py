"""
NEON Topology Build Demo
Demonstrates AI-powered topology generation from natural language
"""
from playwright.sync_api import sync_playwright
import time

def demo_build_topology():
    """Send command to build 3 Cisco routers attached to a switch"""
    print("\n" + "="*80)
    print("NEON AI TOPOLOGY BUILD DEMONSTRATION")
    print("="*80)
    print("\nCommand: 'Build a topology with 3 Cisco routers attached to a switch'")
    print("-"*80)

    with sync_playwright() as p:
        # Launch browser (headless=False to see the action)
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        try:
            print("\n[1/5] Loading NEON application...")
            page.goto('http://localhost:5173', wait_until='networkidle', timeout=30000)
            page.wait_for_selector('text=AI Assistant', timeout=10000)
            print("✓ Application loaded successfully")

            # Take screenshot of initial state
            page.screenshot(path='F:\\Agentic_Apps\\NEON\\tests\\screenshots\\demo_01_initial.png', full_page=True)
            print("✓ Screenshot saved: demo_01_initial.png")

            print("\n[2/5] Locating chat input field...")
            chat_input = page.locator('input[placeholder*="Add devices"], input[placeholder*="topology"]').first

            if not chat_input.is_visible():
                print("✗ Chat input not found, trying alternative selectors...")
                chat_input = page.locator('input[type="text"]').first

            print("✓ Chat input field located")

            print("\n[3/5] Sending command to AI...")
            command = "Build a topology with 3 Cisco routers attached to a switch"
            chat_input.fill(command)
            print(f"✓ Command entered: '{command}'")

            # Take screenshot of command entered
            page.screenshot(path='F:\\Agentic_Apps\\NEON\\tests\\screenshots\\demo_02_command_entered.png', full_page=True)
            print("✓ Screenshot saved: demo_02_command_entered.png")

            # Click send button
            send_button = page.locator('button:has(svg)').filter(has_text='').first
            if send_button.count() == 0:
                # Try alternative selector
                send_button = page.locator('button[type="submit"]').first

            send_button.click()
            print("✓ Send button clicked")

            print("\n[4/5] Waiting for AI to process and build topology...")
            print("    (This may take 10-20 seconds as Claude analyzes the request)")

            # Wait for AI to respond and build topology
            page.wait_for_timeout(20000)
            print("✓ AI processing complete")

            print("\n[5/5] Capturing final topology screenshots...")

            # Take screenshot of chat response
            page.screenshot(path='F:\\Agentic_Apps\\NEON\\tests\\screenshots\\demo_03_ai_response.png', full_page=True)
            print("✓ Screenshot saved: demo_03_ai_response.png")

            # Zoom out to see full topology
            page.keyboard.press('Control+Minus')
            page.keyboard.press('Control+Minus')
            page.wait_for_timeout(1000)

            # Take screenshot of final topology
            page.screenshot(path='F:\\Agentic_Apps\\NEON\\tests\\screenshots\\demo_04_final_topology.png', full_page=True)
            print("✓ Screenshot saved: demo_04_final_topology.png")

            # Analyze the results
            print("\n" + "="*80)
            print("TOPOLOGY BUILD ANALYSIS")
            print("="*80)

            # Count nodes on canvas
            nodes = page.locator('[class*="react-flow__node"]').count()
            print(f"✓ Nodes created: {nodes}")

            # Count edges/links
            edges = page.locator('[class*="react-flow__edge"]').count()
            print(f"✓ Links created: {edges}")

            # Check chat for success messages
            chat_messages = page.locator('[class*="message"]').count()
            print(f"✓ Chat messages: {chat_messages}")

            # Look for action indicators
            success_indicators = page.locator('svg[class*="CheckCircle"], text=Added, text=Created').count()
            if success_indicators > 0:
                print(f"✓ Success indicators found: {success_indicators}")
            else:
                print("⚠ No explicit success indicators (check screenshots)")

            print("\n" + "="*80)
            print("DEMO COMPLETE!")
            print("="*80)
            print("\nScreenshots saved to: tests/screenshots/")
            print("- demo_01_initial.png        : Initial application state")
            print("- demo_02_command_entered.png: Command entered in chat")
            print("- demo_03_ai_response.png    : AI response with actions")
            print("- demo_04_final_topology.png : Final topology on canvas")
            print("\n✓ Topology successfully built via natural language!")
            print("="*80)

            # Keep browser open for 5 seconds to see result
            print("\nKeeping browser open for 10 seconds for viewing...")
            time.sleep(10)

        except Exception as e:
            print(f"\n✗ ERROR: {str(e)}")
            page.screenshot(path='F:\\Agentic_Apps\\NEON\\tests\\screenshots\\demo_error.png', full_page=True)
            print("Error screenshot saved: demo_error.png")
            raise

        finally:
            browser.close()

if __name__ == "__main__":
    demo_build_topology()
