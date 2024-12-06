import requests
import random
BASE_URL = "https://pokeapi.co/api/v2/"

def getPokemon(pokemon):
    """Get pokemon information from the api
    Args:
        pokemon (string): the name of the pokemon that we are fetching data for

    Raises:
        Exception: If the response status code indicates the data could not be fetched

    Returns:
        The response from the endpoint
    """
    url = BASE_URL + 'pokemon/' + pokemon.lower() 
    response = requests.get(url, stream=True, timeout=120)
    if response.status_code != 200:
        raise Exception(f"Failed to get data for {pokemon}: Status code {response.status_code}")
    return response

def getRandomMon():
    """Fetches a random pokemon using random number generation and ids
    
    Raises:
        Exception: If the response status code indicates the data could not be fetched
    
    Returns:
        The response from the endpoint
    """
    #There are 1010 pokemon in total and they can also be searched by id
    random_id = random.randint(1, 1010)
    url = BASE_URL + 'pokemon/' + str(random_id)
    response = requests.get(url, stream=True, timeout=120)
    if response.status_code != 200:
        raise Exception(f"Failed to get data for random opponent: Status code {response.status_code}")
    return response
    