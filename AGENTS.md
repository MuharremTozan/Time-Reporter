# Agentic Development Guide - Time Reporter

This document serves as the source of truth for AI agents operating on this repository. Adhere to these standards strictly to ensure consistency and reliability.

## 🛠 Commands & Automation

### Environment Setup
- **Install Dependencies:** `pip install -r requirements.txt`
- **Virtual Env (Windows):** `python -m venv venv && .\venv\Scripts\activate`

### Verification & Quality
- **Linting:** `ruff check .` (preferred) or `flake8 .`
- **Formatting:** `ruff format .` or `black .`
- **Type Checking:** `mypy src/`
- **Full Test Suite:** `pytest`
- **Single Test File:** `pytest tests/test_module.py`
- **Specific Test Case:** `pytest tests/test_module.py::test_function_name`

### Development
- **Run Application:** `python main.py`
- **Build EXE:** `pyinstaller --noconsole --onefile main.py`

---

## 🎨 Code Style & Conventions

### 1. Imports
- Use absolute imports (e.g., `from src.core import tracker`).
- Order: Standard library → Third-party → Local modules.
- Avoid `from module import *`.

### 2. Naming Conventions
- **Functions & Variables:** `snake_case` (e.g., `get_active_window`).
- **Classes:** `PascalCase` (e.g., `WindowTracker`).
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `POLLING_INTERVAL`).
- **Private Members:** Prefix with underscore (e.g., `_internal_method`).

### 3. Type System
- **Mandatory Type Hints:** All function signatures must include type hints (Python 3.10+ syntax).
- **Complex Types:** Use `list[str]` instead of `List[str]` (modern Python style).
- **Optional Values:** Use `str | None` instead of `Optional[str]`.

### 4. Error Handling
- **Specific Exceptions:** Never use bare `except:`. Always catch specific errors (e.g., `except pywintypes.error`).
- **Graceful Degradation:** The tracker must not crash if a window handle is lost or access is denied. Use logging instead of printing.
- **SQLite Safety:** Use context managers (`with`) for database connections and transactions.

### 5. Project Structure
- `src/core/`: Logic for window tracking and system hooks.
- `src/db/`: Database models and migrations.
- `src/ui/`: UI components using CustomTkinter.
- `src/utils/`: Helper functions (logging, config parsing).
- `tests/`: Pytest test suite mirroring `src/` structure.

---

## 🤖 Agent Protocols (Antigravity Kit)

This repository uses the `.agent/` toolkit. Agents MUST:
1.  **Reference Agents:** Check `.agent/agents/` for specific role instructions before starting tasks (e.g., `backend-specialist.md` for tracker logic).
2.  **Follow Workflows:** Use scripts in `.agent/workflows/` for structured tasks like `/plan`, `/create`, or `/debug`.
3.  **Validate Changes:** Run the validation pipeline (`.agent/scripts/checklist.py`) if available before proposing commits.

---

## 📌 Cursor & Copilot Integration
- If `.cursorrules` or `.opencode` rules exist, they take precedence for LLM behavior.
- Proactively use the `@.agent/` context in your prompts to maintain state.
