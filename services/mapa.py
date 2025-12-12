import requests

def geocode(address: str):
    """Convierte dirección en lat/lon usando Nominatim"""
    url = "https://nominatim.openstreetmap.org/search"
    # User-Agent es obligatorio para no ser bloqueado por OSM
    headers = {"User-Agent": "ReViewsStudentApp/1.0"}
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            raise Exception("Dirección no encontrada")
            
        return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print(f"Error Geocoding: {e}")
        raise e