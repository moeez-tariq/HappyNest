import requests

def get_city_from_coords(lat, lon):
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10"
    response = requests.get(url, headers={'User-Agent': 'YourApp/1.0'})
    data = response.json()
    if 'address' in data:
        city= data['address'].get('city') or data['address'].get('town') or data['address'].get('village')
        if ('City of' in city):
            city=city[8:]
        return city
    return None

# # Usage
city = get_city_from_coords(34.052235,-118.243683)#Los Angelis
city = get_city_from_coords(40.7128, -74.0060)

print(city)  # Should print "New York"

