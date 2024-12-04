import requests
BASE_URL = "https://pokeapi.co/api/v2/"

def getPokemon(pokemon):
    url = BASE_URL + 'pokemon/' + pokemon 
    response = requests.get(url, stream=True, timeout=120)
    return response