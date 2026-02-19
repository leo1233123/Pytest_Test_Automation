import requests

url = "https://api.restful-api.dev/objects"

payload = {
    "name": "Test Object",
    "data": {
        "year": 2024,
        "price": 1000
    }
}

response = requests.post(url, json=payload)

print(response.status_code)
print(response.text)
