import argparse
import copy
import time
import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from solver import solve_urjo

# Load environment variables from the parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

def find_game_grid(page):
    """Find the game grid and return a JS handle to it + grid size."""
    return page.evaluate_handle('''() => {
        const allDivs = Array.from(document.querySelectorAll('div'));
        for (const d of allDivs) {
            const len = d.children.length;
            const sqrtLen = Math.sqrt(len);
            if (sqrtLen < 4 || sqrtLen > 10 || sqrtLen % 2 !== 0) continue;
            if (sqrtLen !== Math.floor(sqrtLen)) continue;
            const children = Array.from(d.children);
            const interactive = children.filter(c => c.tagName === 'BUTTON' || c.querySelector('button') || c.classList.contains('button') || c.classList.contains('o') || c.classList.contains('x'));
            if (interactive.length < len * 0.5) continue;
            const rect = d.getBoundingClientRect();
            if (rect.width > 200 && rect.height > 200) return d;
        }
        return null;
    }''')

def extract_board(page, grid_handle, n):
    """Extract board state (1=Blue/o, 2=Red/x)."""
    return page.evaluate('''([grid, n]) => {
        const children = Array.from(grid.children);
        let g = [], clues = [];
        for (let r = 0; r < n; r++) {
            g.push([]); clues.push([]);
            for (let c = 0; c < n; c++) {
                const cell = children[r * n + c];
                let color = 0;
                const els = [cell, ...cell.querySelectorAll('*')];
                for (const el of els) {
                    if (el.classList.contains('o')) { color = 1; break; } // 1 = Blue
                    if (el.classList.contains('x')) { color = 2; break; } // 2 = Red
                }
                const span = cell.querySelector('span');
                let clueVal = span ? parseInt(span.textContent.trim()) : null;
                g[r].push(color);
                clues[r].push(isNaN(clueVal) ? null : clueVal);
            }
        }
        return { grid: g, clues: clues };
    }''', [grid_handle, n])

def solve_and_apply(page, grid_handle, n):
    """Extract, solve, and apply solution to the current grid."""
    state = extract_board(page, grid_handle, n)
    
    print(f"\n    Board Extraction (1=Blue, 2=Red):")
    for r in range(n):
        print(f"    Row {r}: {state['grid'][r]}")
    
    print("    Solving...")
    sol = solve_urjo(copy.deepcopy(state['grid']), state['clues'])
    if not sol:
        print("    FAILED: Solver could not find a solution.")
        return False

    print("    Applying Solution...")
    for r in range(n):
        for c in range(n):
            if state['grid'][r][c] != 0: continue
            
            target = sol[r][c]
            rect = page.evaluate('''([grid, idx]) => {
                const el = grid.children[idx];
                const r = el.getBoundingClientRect();
                return {x: r.left + r.width/2, y: r.top + r.height/2};
            }''', [grid_handle, r * n + c])
            
            # 2 is Red -> Left Click
            # 1 is Blue -> Right Click
            if target == 2:
                page.mouse.click(rect['x'], rect['y'], button='left')
            else:
                page.mouse.click(rect['x'], rect['y'], button='right')
            time.sleep(0.1)
    return True

def handle_login(page):
    """Handle the email login flow with verbose logging."""
    email = os.getenv("USER_EMAIL")
    if not email:
        print("    [Login] SKIP: No USER_EMAIL in .env")
        return

    print(f"\n[Login] Step 1: Navigating to https://urjo.com/profile/")
    page.goto("https://urjo.com/profile/")
    page.wait_for_load_state("networkidle")
    
    try:
        print("    [Login] Step 2: Checking session state...")
        if page.query_selector("button:has-text('Logout')"):
            print("    [Login] STATUS: Already logged in.")
        else:
            print("    [Login] STATUS: Not logged in. Finding email field...")
            
            # Try to find the specific email input
            selector = "input[placeholder*='Email'], input[name='email'], input[type='email']"
            email_input = page.wait_for_selector(selector, timeout=10000)
            
            print(f"    [Login] Step 3: Typing email '{email}'...")
            email_input.click()
            page.keyboard.type(email, delay=50)
            
            # Verification
            typed_val = email_input.evaluate("el => el.value")
            print(f"    [Login] Step 4: Verified input content: '{typed_val}'")
            
            if typed_val != email:
                print("    [Login] WARNING: Content mismatch, forcing fill...")
                email_input.fill(email)

            # Submit
            btn_selector = "button:has-text('Continue'), button:has-text('Save'), button[type='submit']"
            print(f"    [Login] Step 5: Clicking submit button ({btn_selector})...")
            page.click(btn_selector, force=True)
            
            print("\n" + "!" * 60)
            print("  ACTION REQUIRED: Enter the verification code in the browser.")
            print("!" * 60 + "\n")
            
            # Wait for Logout button
            print("    [Login] Step 6: Waiting for Logout button to appear...")
            page.wait_for_selector("button:has-text('Logout')", timeout=120000)
            print("    [Login] Step 7: Success! Logged in.")
        
        print("    [Login] Step 8: Returning to game...")
        page.goto("https://urjo.com/")
        page.wait_for_load_state("networkidle")
        
    except Exception as e:
        print(f"    [Login] !!! SNAG: {e}")
        page.screenshot(path="login_debug.png")
        input("    [Login] Paused. Check 'login_debug.png' and press Enter to skip/continue...")

def run(count):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 900})
        
        print("="*40 + f"\nURJO BOT: SOLVING {count} PUZZLES\n" + "="*40)
        
        # 0. Handle Login
        handle_login(page)
        
        page.goto("https://urjo.com/")
        time.sleep(1)
        
        # 1. Start
        print("[1] Clicking Start...")
        try:
            page.click("button:has-text('Start')", timeout=5000)
        except:
            print("    Start button not found, assuming game already started.")
        time.sleep(2)
            
        # 2. Solid mode (Sticky settings, only check once)
        print("[2] Ensuring Solid Mode...")
        page.evaluate("window.scrollTo(0, 1000)") 
        time.sleep(0.5)
        
        is_checked = page.evaluate('''() => {
            const labels = Array.from(document.querySelectorAll('label'));
            const solidLabel = labels.find(l => l.textContent.includes('Solid'));
            if (!solidLabel) return false;
            const input = solidLabel.querySelector('input') || solidLabel.parentElement.querySelector('input');
            return input ? input.checked : false;
        }''')
        
        if not is_checked:
            page.click("text=Solid")
            print("    Toggled Solid mode ON.")
        else:
            print("    Solid mode already ON.")
            
        time.sleep(0.5)
        page.evaluate("window.scrollTo(0, 0)") 
        time.sleep(1)

        # 3. Main loop
        for i in range(count):
            print(f"\n--- Puzzle {i+1}/{count} ---")
            
            # Find grid
            grid_handle = find_game_grid(page)
            if not grid_handle:
                print("    Error: Could not find grid. Retrying...")
                time.sleep(2)
                grid_handle = find_game_grid(page)
                if not grid_handle:
                    print("    Critical Error: Grid not found.")
                    break
            
            n = int(page.evaluate('(g) => Math.sqrt(g.children.length)', grid_handle))
            success = solve_and_apply(page, grid_handle, n)
            
            if success and i < count - 1:
                print("    Puzzle solved! Waiting for 'Next Challenge' button...")
                try:
                    next_btn = page.wait_for_selector("button:has-text('Next Challenge')", timeout=10000)
                    if next_btn:
                        next_btn.click()
                        print("    Clicked 'Next Challenge'.")
                        time.sleep(2) # Wait for new grid to load
                except Exception as e:
                    print(f"    Warning: 'Next Challenge' button didn't appear as expected: {e}")
                    # Try to see if grid changed anyway or if we need to click something else
            elif not success:
                print("    Skipping next challenge due to failure.")
                break

        print("\n[Done] All requested puzzles completed.")
        input("Press Enter to close...")
        browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automate Urjo puzzles.")
    parser.add_argument("--count", type=int, default=1, help="Number of puzzles to solve.")
    args = parser.parse_args()
    
    run(args.count)
