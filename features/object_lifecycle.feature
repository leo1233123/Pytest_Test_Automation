Feature: Object Lifecycle Management
As a QE Intern
I want to validate the full object lifecycle
So that I can ensure the API behaves correctly across integrated calls
# Positive Scenario (Happy Path)
Scenario: Successfully create, retrieve, update and delete an object
Given I have a valid object payload
When I send a POST request to create the object
Then the response status code should be 200
And the response should contain an object id
When I send a GET request using the stored object id
Then the response status code should be 200
And the response name should match the created object name
When I update the object with a new name
Then the response status code should be 200
And the response name should reflect the updated value
When I send a DELETE request using the stored object id
Then the response status code should be 200
When I send a GET request using the deleted object id
Then the response status code should be 404
# Negative Scenarios
Scenario: Retrieve non-existing object
Given I have a non-existing object id
When I send a GET request using that id
Then the response status code should be 404
Scenario: Create object with invalid payload
Given I have an invalid object payload
When I send a POST request to create the object
Then the response status code should indicate a client error