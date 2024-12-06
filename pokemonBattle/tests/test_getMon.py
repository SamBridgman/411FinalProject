import pytest
import requests
from unittest.mock import Mock
from pokemonBattle.getMon import getPokemon, getRandomMon 

BASE_URL = "https://pokeapi.co/api/v2/"

def test_getPokemon_success(mocker):
    # Mocking the requests.get method
    mock_response = Mock()
    mock_response.status_code = 200
    mocker.patch("requests.get", return_value=mock_response)

    pokemon_name = "pikachu"
    response = getPokemon(pokemon_name)

    # Assertions
    requests.get.assert_called_once_with(BASE_URL + f'pokemon/{pokemon_name}', stream=True, timeout=120)
    assert response.status_code == 200

def test_getPokemon_failure(mocker):
    # Mocking the requests.get method to simulate a failure
    mock_response = Mock()
    mock_response.status_code = 404
    mocker.patch("requests.get", return_value=mock_response)

    pokemon_name = "unknown_pokemon"
    with pytest.raises(Exception, match=f"Failed to get data for {pokemon_name}: Status code 404"):
        getPokemon(pokemon_name)

def test_getRandomMon(mocker):
    # Mocking the requests.get method
    mock_response = Mock()
    mock_response.status_code = 200
    mocker.patch("requests.get", return_value=mock_response)

    response = getRandomMon()

    # Assertions
    requests.get.assert_called_once()
    assert response.status_code == 200