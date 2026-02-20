import pytest
from pytest_bdd import scenarios, given, when, then
from api.client import ObjectApi
import atexit
import os

BASE_URL = "https://api.restful-api.dev/objects"
api = ObjectApi(BASE_URL)

# Load feature file
scenarios("../features/object_lifecycle.feature")

# Results collector
results = []

# Ensure results folder exists
RESULTS_FOLDER = os.path.join(os.path.dirname(__file__), "..", "results")
os.makedirs(RESULTS_FOLDER, exist_ok=True)

from utils.html_report import generate_html

# Register HTML generation at exit
atexit.register(lambda: generate_html(results))

@pytest.fixture
def context():
    return {}

# ---------------------------
# HELPER
# ---------------------------
def safe_json(response):
    """Extract JSON safely from FakeObjectApi or requests.Response."""
    try:
        return response.json()
    except Exception:
        if hasattr(response, "text"):
            return {"raw_text": response.text}
        return {"raw_text": str(response)}

# ---------------------------
# GIVEN STEPS
# ---------------------------
@given("I have a valid object payload")
def valid_object_payload(context):
    context["payload"] = {
        "name": "Test Object",
        "data": {
            "year": 2024,
            "price": 1000
        }
    }

@given("I have an invalid object payload")
def invalid_object_payload(context):
    context["payload"] = {}

@given("I have a non-existing object id")
def non_existing_object_id(context):
    context["object_id"] = "999999999"

# ---------------------------
# WHEN STEPS
# ---------------------------
@when("I send a POST request to create the object")
def create_object(context):
    context["action"] = "POST request to create the object"   # ← add this
    response = api.post(context["payload"])
    context["response"] = response
    if response.status_code == 200:
        json_data = safe_json(response)
        context["object_id"] = json_data["id"]
        context["created_name"] = json_data["name"]

@when("I send a GET request using the stored object id")
def get_object(context):
    context["action"] = "GET request using the stored object id"   # ← add this
    response = api.get(context["object_id"])
    context["response"] = response

@when("I update the object with a new name")
def update_object(context):
    context["action"] = "PUT request to update the object"   # ← add this
    updated_payload = {"name": "Updated Object Name"}
    response = api.put(context["object_id"], updated_payload)
    context["response"] = response
    context["updated_name"] = updated_payload["name"]

@when("I send a DELETE request using the stored object id")
def delete_object(context):
    context["action"] = "DELETE request using the stored object id"   # ← add this
    response = api.delete(context["object_id"])
    context["response"] = response

@when("I send a GET request using the deleted object id")
def get_deleted_object(context):
    context["action"] = "GET request using the deleted object id"   # ← add this
    response = api.get(context["object_id"])
    context["response"] = response

@when("I send a GET request using that id")
def get_non_existing_object(context):
    context["action"] = "GET request using non-existing id"   # ← add this
    response = api.get(context["object_id"])
    context["response"] = response

# ---------------------------
# THEN STEPS
# ---------------------------
@then("the response status code should be 200")
def check_status_200(context):
    passed = context["response"].status_code == 200
    data = safe_json(context["response"])
    results.append({
        "scenario": "Successfully create, retrieve, update and delete an object",
        "action": context.get("action", "N/A"), 
        "step_description": f"Status code is {context['response'].status_code}",
        "passed": passed,
        "data": data
    })
    assert passed

@then("the response should contain an object id")
def check_object_id(context):
    json_data = safe_json(context["response"])
    passed = "id" in json_data and json_data["id"]
    results.append({
        "scenario": "Successfully create, retrieve, update and delete an object",
        "action": context.get("action", "N/A"), 
        "step_description": "Check response contains object id",
        "passed": passed,
        "data": json_data
    })
    assert passed

@then("the response name should match the created object name")
def check_created_name(context):
    json_data = safe_json(context["response"])
    passed = json_data.get("name") == context.get("created_name")
    results.append({
        "scenario": "Successfully create, retrieve, update and delete an object",
        "action": context.get("action", "N/A"), 
        "step_description": "Check created object name",
        "passed": passed,
        "data": json_data
    })
    assert passed

@then("the response name should reflect the updated value")
def check_updated_name(context):
    json_data = safe_json(context["response"])
    passed = json_data.get("name") == context.get("updated_name")
    results.append({
        "scenario": "Successfully create, retrieve, update and delete an object",
        "action": context.get("action", "N/A"), 
        "step_description": "Check updated object name",
        "passed": passed,
        "data": json_data
    })
    assert passed

@then("the response status code should be 404")
def check_status_404(context):
    passed = context["response"].status_code == 404
    data = safe_json(context["response"])
    results.append({
        "scenario": "Retrieve non-existing object",
        "action": context.get("action", "N/A"), 
        "step_description": "Status code is 404",
        "passed": passed,
        "data": data
    })
    assert passed

@then("the response status code should indicate a client error")
def check_client_error(context):
    status = context["response"].status_code
    passed = 400 <= status < 500
    data = safe_json(context["response"])
    results.append({
        "scenario": "Create object with invalid payload",
        "action": context.get("action", "N/A"), 
        "step_description": f"Client error status: {status}",
        "passed": passed,
        "data": data
    })
    assert passed


