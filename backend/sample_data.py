import requests

url = "http://127.0.0.1:8000/ingest"

data = [
    ("DB_MAIN", "Database crash"),
    ("CACHE_1", "Cache miss spike"),
    ("API_1", "Latency issue"),
]

for comp, msg in data:
    requests.post(f"{url}?component_id={comp}&message={msg}")

print("Sample data sent")