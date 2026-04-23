from playwright.sync_api import sync_playwright
import time
import copy
from solver import solve_urjo

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

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 900})
        
        print("="*40 + "\nURJO BOT: CORRECTED MAPPING\n" + "="*40)
        page.goto("https://urjo.com/")
        time.sleep(1)
        
        # 1. Start
        print("[1] Clicking Start...")
        try:
            page.click("button:has-text('Start')", timeout=5000)
        except:
            print("    Start button not found, assuming game already started.")
        time.sleep(2)
            
        # 2. Solid mode & Scroll Up
        print("[2] Toggling Solid Mode & Scrolling Up...")
        page.evaluate("window.scrollTo(0, 1000)") 
        time.sleep(0.5)
        
        # Check if checked first
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
        
        # 3. Detect
        grid_handle = find_game_grid(page)
        if not grid_handle:
            print("    Error: Could not find grid.")
            return
            
        n = int(page.evaluate('(g) => Math.sqrt(g.children.length)', grid_handle))
        state = extract_board(page, grid_handle, n)
        
        print("\n[3] Board Extraction (1=Blue, 2=Red):")
        for r in range(n):
            print(f"    Row {r}: {state['grid'][r]}")
        
        # 4. Solve
        print("\n[4] Solving...")
        sol = solve_urjo(copy.deepcopy(state['grid']), state['clues'])
        if not sol:
            print("    FAILED: Solver could not find a solution.")
            return

        # 5. Apply
        print("\n[5] Applying Solution...")
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
                    print(f"    ({r},{c}) -> RED (Left Click)")
                    page.mouse.click(rect['x'], rect['y'], button='left')
                else:
                    print(f"    ({r},{c}) -> BLUE (Right Click)")
                    page.mouse.click(rect['x'], rect['y'], button='right')
                time.sleep(0.2)
        
        print("\n[6] Done!")
        input("Press Enter to close...")
        browser.close()

if __name__ == "__main__":
    run()
