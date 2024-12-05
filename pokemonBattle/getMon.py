import requests
import random
BASE_URL = "https://pokeapi.co/api/v2/"

def getPokemon(pokemon):
    url = BASE_URL + 'pokemon/' + pokemon.lower() 
    response = requests.get(url, stream=True, timeout=120)
    if response.status_code != 200:
        raise Exception(f"Failed to get data for {pokemon}: Status code {response.status_code}")
    return response

def getRandomMon():
    #There are 1010 pokemon in total and they can also be searched by id
    random_id = random.randint(1, 1010)
    url = BASE_URL + 'pokemon/' + str(random_id)
    response = requests.get(url, stream=True, timeout=120)
    return response
    