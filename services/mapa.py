import requests

def geocode(city: str):
    url = "https://nominatim.openstreetmap.org/search"
    
    params = {
        "q": city,
        "format": "json",
        "limit": 1
    }

    headers = {
        "User-Agent": "FastAPI-App"
    }

    response = requests.get(url, params=params, headers=headers, timeout=10)

    if response.status_code != 200:
        raise Exception("Error al conectar con el servicio de geocoding")

    data = response.json()

    if not data:
        raise Exception("Ciudad o país no encontrado")

    return float(data[0]["lat"]), float(data[0]["lon"])
