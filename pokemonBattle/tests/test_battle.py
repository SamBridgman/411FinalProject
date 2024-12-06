import pytest
from unittest.mock import Mock
from pokemonBattle.battle import (
    PokemonBattle,
    getStats,
    getAttackPower,
    getSpeedMult,
    getType,
    getTypingInformation,
    getBestDamageMultiplier,
)
from pokemonBattle.getMon import getPokemon


# Mock data for API responses
MOCK_POKEMON_DATA = {
    "pikachu": {
        "stats": [
            {"stat": {"name": "hp"}, "base_stat": 35},
            {"stat": {"name": "attack"}, "base_stat": 55},
            {"stat": {"name": "defense"}, "base_stat": 40},
            {"stat": {"name": "special-attack"}, "base_stat": 50},
            {"stat": {"name": "special-defense"}, "base_stat": 50},
            {"stat": {"name": "speed"}, "base_stat": 90}
        ],
        "types": [{"type": {"name": "electric"}}]
    },
    "charmander": {
        "stats": [
            {"stat": {"name": "hp"}, "base_stat": 39},
            {"stat": {"name": "attack"}, "base_stat": 52},
            {"stat": {"name": "defense"}, "base_stat": 43},
            {"stat": {"name": "special-attack"}, "base_stat": 60},
            {"stat": {"name": "special-defense"}, "base_stat": 50},
            {"stat": {"name": "speed"}, "base_stat": 65}
        ],
        "types": [{"type": {"name": "fire"}}]
    }
}


@pytest.fixture
def mock_getPokemon(mocker):
    """Fixture to mock the getPokemon function."""
    def mock_function(pokemon):
        response = Mock()
        if pokemon.lower() in MOCK_POKEMON_DATA:
            response.status_code = 200
            response.json.return_value = MOCK_POKEMON_DATA[pokemon.lower()]
        else:
            response.status_code = 404
            response.json.return_value = {}
        return response

    mocker.patch("pokemonBattle.getMon.getPokemon", side_effect=mock_function)


def test_getStats(mock_getPokemon):
    stats = getStats("pikachu")
    assert stats["hp"] == 35
    assert stats["attack"] == 55
    assert stats["speed"] == 90


def test_getAttackPower():
    attacker = {"attack": 55, "special-attack": 50}
    defender = {"defense": 40, "special-defense": 30}
    assert getAttackPower(attacker, defender) == 20


def test_getSpeedMult():
    assert getSpeedMult(90, 60) == 1.2
    assert getSpeedMult(60, 90) == 1.0


def test_getType(mock_getPokemon):
    types = getType("pikachu")
    assert "electric" in types


def test_getTypingInformation(mocker):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "name": "electric",
        "damage_relations": {
            "double_damage_to": [{"name": "water"}],
            "half_damage_to": [{"name": "electric"}],
            "no_damage_to": []
        }
    }
    mocker.patch("requests.get", return_value=mock_response)

    typing_info = getTypingInformation("electric")
    assert typing_info["type"] == "electric"
    assert "water" in typing_info["damage_relations"]["double_damage_to"]


def test_getBestDamageMultiplier():
    attacking = [{"type": "electric", "damage_relations": {"double_damage_to": ["water"]}}]
    defending = [{"type": "water", "damage_relations": {}}]

    assert getBestDamageMultiplier(attacking, defending) == 2.0


def test_PokemonBattle(mock_getPokemon):
    result = PokemonBattle("pikachu", "charmander")
    assert result in ["User", "Enemy"]  