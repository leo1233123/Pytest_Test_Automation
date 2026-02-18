import requests
import pytest
from pytest_bdd import scenarios, given, when, then

# Load the feature file
scenarios("../features/object_lifecycle.feature")

BASE_URL = "https://api.restful-api.dev/objects"


@pytest.fixture
def context():
    return {}


# ---------------------------
# POSITIVE SCENARIOS
# ---------------------------

# ---------------------------
# Scenario: Successfully create, retrieve, update and delete an object
# ---------------------------

@given("I have a valid object payload")
def valid_object_payload(context):
    context["payload"] = {
        "name": "Test Object",
        "data": {
            "year": 2024,
            "price": 1000,
        }
    }

@when("I send a POST request to create the object")
def create_object(context):
    response = requests.post(BASE_URL, json=context["payload"])
    context["response"] = response

    if response.status_code == 200:
        json_data = response.json()
        context["object_id"] = json_data["id"]
        context["created_name"] = json_data["name"]


@then("the response status code should be 200")
def check_status_200(context):
    assert context["response"].status_code == 200
    assert context["response"].elapsed.total_seconds() < 2  # SLA check

@then("the response should contain an object id")
def check_object_id(context):
    json_data = context["response"].json()
    assert "id" in json_data
    assert isinstance(json_data["id"], str)  # type validation
    assert json_data["id"]  # not empty

@when("I send a GET request using the stored object id")
def get_object(context):
    url = f"{BASE_URL}/{context['object_id']}"
    response = requests.get(url)
    context["response"] = response

@then("the response name should match the created object name")
def check_created_name(context):
    json_data = context["response"].json()
    expected = context["created_name"]
    actual = json_data["name"]
    assert actual == expected, f"Expected '{expected}', got '{actual}'"

@when("I update the object with a new name")
def update_object(context):
    updated_payload = {
        "name": "Updated Object Name"
    }

    url = f"{BASE_URL}/{context['object_id']}"
    response = requests.put(url, json=updated_payload)

    context["response"] = response
    context["updated_name"] = updated_payload["name"]

@then("the response name should reflect the updated value")
def check_updated_name(context):
    json_data = context["response"].json()
    assert json_data["name"] == context["updated_name"]

@when("I send a DELETE request using the stored object id")
def delete_object(context):
    url = f"{BASE_URL}/{context['object_id']}"
    response = requests.delete(url)
    context["response"] = response

@when("I send a GET request using the deleted object id")
def get_deleted_object(context):
    url = f"{BASE_URL}/{context['object_id']}"
    response = requests.get(url)
    context["response"] = response



# ---------------------------
# NEGATIVE SCENARIOS
# ---------------------------


# ---------------------------
# Scenario: Retrieve non-existing object
# ---------------------------

@given("I have a non-existing object id")
def non_existing_object_id(context):
    context["object_id"] = "999999999"

@when("I send a GET request using that id")
def get_non_existing_object(context):
    url = f"{BASE_URL}/{context['object_id']}"
    response = requests.get(url)
    context["response"] = response

@then("the response status code should be 404")
def check_status_404(context):
    assert context["response"].status_code == 404


# ---------------------------
# Scenario: Create object with invalid payload
# ---------------------------

@given("I have an invalid object payload")
def invalid_object_payload(context):
    context["payload"] = {}  # empty payload → should trigger 4xx


@then("the response status code should indicate a client error")
def check_client_error(context):
    assert 400 <= context["response"].status_code < 500


