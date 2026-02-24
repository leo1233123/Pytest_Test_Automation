import pytest
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root automatically
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

results = []

# Hook to capture test results
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call":
        step_name = getattr(item, "step_name", item.name)
        context_data = getattr(item, "context_data", None)

        results.append({
            "scenario": item.name,
            "step": step_name,
            "passed": rep.passed,
            "data": context_data
        })