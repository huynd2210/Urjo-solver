# Urjo Solver Bot - Project Overview

This project is an automated solver for the logic puzzles at [urjo.com](https://urjo.com/). It uses a Python-based backtracking solver and Playwright for browser automation.

## Tech Stack
- **Language**: Python 3.12+
- **Automation**: Playwright (Python Sync API)
- **Logic**: Backtracking search with constraint satisfaction.

## Game Rules (Urjo)
1. **Balance**: Every row and column must contain an equal number of Red and Blue spots.
2. **Uniqueness**: No two adjacent rows or columns can be identical.
3. **Numeric Clues**: Some cells contain numbers. A number `N` indicates that exactly `N` of the 8 surrounding neighbors (including diagonals) must share the same color as the numbered cell.

## Project Structure
- `backend/solver.py`: Core logic. Contains the `solve_urjo` function which takes a grid and clues and returns a unique solution.
- `backend/bot.py`: Automation script. Handles navigation, grid discovery, "Solid" mode configuration, and interaction.
- `backend/test_solver.py`: Unit tests for the solver logic.

## Logic & Configuration
### Color Mapping
- `0`: Empty
- `1`: Blue (represented by CSS class `o`)
- `2`: Red (represented by CSS class `x`)

### Interaction Mode
The bot uses **"Solid" spot style** (enabled via the site settings):
- **Left-Click**: Sets a cell to **Red (2)**.
- **Right-Click**: Sets a cell to **Blue (1)**.

### Extraction Heuristics
- **Grid Discovery**: The bot identifies the game grid by scanning for `div` elements that contain exactly $N^2$ interactive children (buttons or specific styled divs) where $N$ is an even number between 4 and 10.
- **Color Detection**: Inspects the `classList` of cell elements for `o` or `x`.
- **Clue Detection**: Parses the `textContent` of `<span>` elements inside cells.

## Commands
- **Solve Puzzles**: `python backend/bot.py --count <number>`
  - `--count`: Number of consecutive puzzles to solve. The bot will automatically click "Next Challenge".

## Key Logic Notes for Future LLMs
- **8-Neighbor Rule**: Numeric clues are always 8-way (King's move in chess).
- **Coordinate System**: The bot uses `getBoundingClientRect()` via `page.evaluate` to get precise center coordinates for clicking, ensuring compatibility even if the page scrolls or re-renders.
- **Solid Mode Toggle**: The bot programmatically checks the "Solid" checkbox. If it's already checked, it avoids clicking it to prevent toggling it off.
- **Solvability**: The solver uses a deep copy of the grid to avoid in-place corruption during backtracking.
- **Login Flow**: The bot can handle email-based authentication by navigating to `/profile/`. It reads the target email from a `.env` file and pauses for manual verification code entry.

## Setup Requirements
- **Environment**: Create a `.env` file in the root directory with `USER_EMAIL=your_email@example.com`.
- **Dependencies**: `pip install python-dotenv`
