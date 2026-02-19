import pytest
from utils.html_report import generate_html

results = []

# Hook to capture test results
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    
    # Only record actual test calls
    if rep.when == "call":
        # Attempt to capture step name & context data
        step_name = getattr(item, "step_name", item.name)
        context_data = getattr(item, "context_data", None)
        
        results.append({
            "scenario": item.name,
            "step": step_name,
            "passed": rep.passed,
            "data": context_data
        })

# Generate HTML after session
def pytest_sessionfinish(session, exitstatus):
    generate_html(results)
