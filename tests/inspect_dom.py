"""
DOM Inspector for NEON Application
Helps identify correct selectors for testing
"""
from playwright.sync_api import sync_playwright

def inspect_frontend():
    """Inspect frontend DOM structure"""
    print("Inspecting NEON Frontend DOM...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto('http://localhost:5173', wait_until='networkidle', timeout=30000)

        # Wait for app to render
        page.wait_for_timeout(5000)

        # Get full HTML
        html_content = page.content()

        # Take screenshot
        page.screenshot(path='F:\\Agentic_Apps\\NEON\\tests\\screenshots\\full_page.png', full_page=True)

        # Find all headings
        print("\n--- Headings ---")
        headings = page.locator('h1, h2, h3').all()
        for heading in headings:
            try:
                text = heading.text_content()
                print(f"  {heading.evaluate('el => el.tagName')}: {text}")
            except:
                pass

        # Find all buttons
        print("\n--- Buttons ---")
        buttons = page.locator('button').all()
        print(f"  Found {len(buttons)} buttons")
        for i, btn in enumerate(buttons[:10]):  # First 10
            try:
                text = btn.text_content()
                if text and text.strip():
                    print(f"  Button {i+1}: {text.strip()[:50]}")
            except:
                pass

        # Find main containers
        print("\n--- Main Containers ---")
        containers = page.locator('[class*="flex"]').all()
        print(f"  Found {len(containers)} flex containers")

        # Check for specific elements
        print("\n--- Key Elements ---")

        # NEON header
        neon_text = page.locator('text=NEON').count()
        print(f"  'NEON' text found: {neon_text} times")

        # AI Assistant
        ai_text = page.locator('text=AI Assistant').count()
        print(f"  'AI Assistant' found: {ai_text} times")

        # Input fields
        inputs = page.locator('input').count()
        print(f"  Input fields: {inputs}")

        # Canvas/ReactFlow
        react_flow = page.locator('[class*="react-flow"]').count()
        print(f"  ReactFlow elements: {react_flow}")

        # Sidebar check
        print("\n--- Sidebar Analysis ---")
        sidebars = page.locator('[class*="w-64"], [class*="w-80"], [class*="sidebar"]').all()
        print(f"  Found {len(sidebars)} potential sidebar elements")

        for i, sidebar in enumerate(sidebars[:3]):
            try:
                classes = sidebar.get_attribute('class')
                print(f"  Sidebar {i+1} classes: {classes}")
            except:
                pass

        browser.close()

        print("\n✓ Inspection complete. Check screenshots/full_page.png")

if __name__ == "__main__":
    inspect_frontend()
