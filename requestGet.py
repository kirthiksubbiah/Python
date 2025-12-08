import requests

url = "https://jsonplaceholder.typicode.com/posts"
response = requests.get(url, verify=False)

print(response.status_code)
print(response.text[:200])    
