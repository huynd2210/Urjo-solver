import argparse
import copy
import time
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from solver import solve_urjo

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

class UrjoBot:
    def __init__(self, page, email=None):
        self.page = page
        self.email = email
        self.grid_handle = None
        self.n = 0

    def login(self):
        """Handles the email-based login flow."""
        if not self.email:
            print("    [Login] SKIP: No email provided.")
            return

        print(f"\n[Login] Step 1: Navigating to profile...")
        # Increase timeout to 60s for slow loads
        self.page.goto("https://urjo.com/profile/", timeout=60000)
        self.page.wait_for_load_state("domcontentloaded")

        if self.page.query_selector("button:has-text('Logout')"):
            print("    [Login] STATUS: Already logged in.")
        else:
            print(f"    [Login] STATUS: Not logged in. Entering email: {self.email}")
            selector = "input[name='email'], input[placeholder*='Email'], input[type='email'], input"
            email_input = self.page.wait_for_selector(selector, timeout=10000)
            
            # Focused typing for better React compatibility
            email_input.click()
            self.page.keyboard.type(self.email, delay=50)
            
            print("    [Login] Step 2: Submitting email...")
            self.page.click("button:has-text('Continue'), button:has-text('Save'), button[type='submit']")
            
            print("\n" + "!" * 60)
            print("  ACTION REQUIRED: Enter the verification code in the browser.")
            print("!" * 60 + "\n")
            
            # Wait for Logout button
            print("    [Login] Step 3: Waiting for login success (Logout button)...")
            self.page.wait_for_selector("button:has-text('Logout')", timeout=120000)
            print("    [Login] STATUS: Success detected.")

        print("    [Login] Step 4: Returning to main page...")
        self.page.goto("https://urjo.com/", timeout=60000)
        self.page.wait_for_load_state("domcontentloaded")

    def prepare_game(self):
        """Handles any 'Start' type buttons and ensures settings are correct."""
        # 1. Look for Start/Resume/Next Challenge button
        starter_btn = self.page.query_selector("button:has-text('Start'), button:has-text('Resume'), button:has-text('Next Challenge')")
        if starter_btn:
            btn_text = starter_btn.inner_text().strip()
            print(f"[Game] Step 5: Clicking {btn_text}...")
            starter_btn.click()
            time.sleep(2)

        # 2. Ensure Solid mode
        print("[Game] Step 6: Ensuring Solid mode settings...")
        self.page.evaluate("window.scrollTo(0, 1000)")
        time.sleep(0.5)

        is_solid = self.page.evaluate('''() => {
            const labels = Array.from(document.querySelectorAll('label'));
            const solidLabel = labels.find(l => l.textContent.includes('Solid'));
            const input = solidLabel?.querySelector('input') || solidLabel?.parentElement?.querySelector('input');
            return input?.checked || false;
        }''')

        if not is_solid:
            self.page.click("text=Solid")
            print("    [Game] Solid mode toggled ON.")
        else:
            print("    [Game] Solid mode already active.")
        
        self.page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1)

    def find_grid(self):
        """Finds the game grid handle."""
        self.grid_handle = self.page.evaluate_handle('''() => {
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
        
        element = self.grid_handle.as_element()
        if element:
            self.n = int(self.page.evaluate('(g) => Math.sqrt(g.children.length)', self.grid_handle))
            return True
        return False

    def solve_and_apply(self):
        """Full cycle: extract, solve, and apply."""
        if not self.find_grid():
            print("    [Error] Grid not found on screen.")
            return False

        # Extract
        state = self.page.evaluate('''([grid, n]) => {
            const children = Array.from(grid.children);
            let g = [], clues = [];
            for (let r = 0; r < n; r++) {
                g.push([]); clues.push([]);
                for (let c = 0; c < n; c++) {
                    const cell = children[r * n + c];
                    let color = 0;
                    const els = [cell, ...cell.querySelectorAll('*')];
                    for (const el of els) {
                        if (el.classList.contains('o')) { color = 1; break; } // Blue
                        if (el.classList.contains('x')) { color = 2; break; } // Red
                    }
                    const span = cell.querySelector('span');
                    let clueVal = span ? parseInt(span.textContent.trim()) : null;
                    g[r].push(color);
                    clues[r].push(isNaN(clueVal) ? null : clueVal);
                }
            }
            return { grid: g, clues: clues };
        }''', [self.grid_handle, self.n])

        print(f"    [Solve] Detected {self.n}x{self.n} grid.")
        
        # Solve
        sol = solve_urjo(copy.deepcopy(state['grid']), state['clues'])
        if not sol:
            print("    [Error] Solver failed to find a solution.")
            return False

        # Save data for AI training
        self.save_puzzle_data(state, sol)

        # Apply
        print(f"    [Apply] Clicking cells...")
        for r in range(self.n):
            for c in range(self.n):
                if state['grid'][r][c] != 0: continue
                
                target = sol[r][c]
                rect = self.page.evaluate('''([grid, idx]) => {
                    const el = grid.children[idx];
                    const r = el.getBoundingClientRect();
                    return {x: r.left + r.width/2, y: r.top + r.height/2};
                }''', [self.grid_handle, r * self.n + c])
                
                button = 'left' if target == 2 else 'right'
                self.page.mouse.click(rect['x'], rect['y'], button=button)
                time.sleep(0.15)
        return True

    def save_puzzle_data(self, state, solution):
        """Saves the puzzle and solution for AI training."""
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        os.makedirs(data_dir, exist_ok=True)
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "size": self.n,
            "input_grid": state['grid'],
            "clues": state['clues'],
            "solution": solution
        }
        
        file_path = os.path.join(data_dir, "puzzles.jsonl")
        with open(file_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
        print(f"    [Data] Saved puzzle to {file_path}")

    def next_challenge(self):
        """Moves to the next puzzle."""
        print("[Game] Waiting for next challenge...")
        try:
            next_btn = self.page.wait_for_selector("button:has-text('Next Challenge')", timeout=15000)
            next_btn.click()
            time.sleep(2)
        except Exception as e:
            print(f"    [Warning] Failed to find Next Challenge button: {e}")

def run(count):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.set_viewport_size({"width": 1280, "height": 900})
        
        bot = UrjoBot(page, email=os.getenv("USER_EMAIL"))
        
        print("="*40 + f"\nURJO BOT: {count} PUZZLES\n" + "="*40)
        
        # 1. Login
        bot.login()
        
        # 2. Prep
        bot.prepare_game()

        while True:
            # 3. Solve Loop
            for i in range(count):
                print(f"\n--- Puzzle {i+1}/{count} ---")
                success = bot.solve_and_apply()
                
                if success and i < count - 1:
                    bot.next_challenge()
                elif not success:
                    break

            print("\n[Batch Done] Successfully completed the requested puzzles.")
            ans = input("\n[Prompt] Continue solving? (Enter a number for more puzzles, or 'q' to quit): ").strip().lower()
            
            if ans == 'q' or ans == '':
                break
            
            try:
                count = int(ans)
                # Ensure we move to the next puzzle before starting the next batch
                bot.next_challenge()
            except ValueError:
                print("    Invalid input. Exiting...")
                break

        print("\n[Exit] Closing bot. Goodbye!")
        browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=1)
    args = parser.parse_args()
    run(args.count)
