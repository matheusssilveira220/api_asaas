import requests

url = "https://api.asaas.com/v3/customers"

headers = {
    "accept": "application/json",
    "access_token": "$aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6Ojg2NDVhNjk3LTMyNjktNDc4My1hZWVkLWY0MDZkOTgyMzQ4Zjo6JGFhY2hfZTIxYTMzZmUtMmRkNS00MDQwLWE0NTUtOGMyMjg4NjQ5ODBj"
}

response = requests.get(url, headers=headers)

print(response.status_code)