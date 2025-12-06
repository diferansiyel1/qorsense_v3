import requests
import time

try:
    print("Testing GET http://127.0.0.1:8000/sensors...")
    start = time.time()
    response = requests.get("http://127.0.0.1:8000/sensors", timeout=5)
    end = time.time()
    print(f"Status Code: {response.status_code}")
    print(f"Time: {end - start:.2f}s")
    print("Response JSON:")
    print(response.json())
except Exception as e:
    print(f"Error: {e}")
