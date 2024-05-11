import requests

url = "http://172.17.240.85:8181/stable_code_instruct_3b"

payload = {
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful and polite code assistant",
        },
        {
            "role": "user",
            "content": "Write a function that takes a list of integers and returns the sum of all the integers in the list"
        },
    ]
}

headers = {
    'Content-Type': 'application/json'
}

result = requests.post(url, headers=headers, json=payload)
print(result.json())