import requests

BASE_URL = "https://renuevochurch.onrender.com"


class ApiClient:

    @staticmethod
    def get(endpoint, params=None):
        url = f"{BASE_URL}{endpoint}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def post(endpoint, data=None):
        url = f"{BASE_URL}{endpoint}"
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def put(endpoint, data=None):
        url = f"{BASE_URL}{endpoint}"
        response = requests.put(url, json=data)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def delete(endpoint):
        url = f"{BASE_URL}{endpoint}"
        response = requests.delete(url)
        response.raise_for_status()
        return response.json()
