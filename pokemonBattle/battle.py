from pokemonBattle.getMon import getPokemon
import requests

def PokemonBattle(user_mon, enemy_mon):
    """The main battle function which simulates a battle between two pokemon by comparing stats and typing!

    Args:
        user_mon string: name of the user's pokemon
        enemy_mon string: name of the enemey's pokemon

    Returns:
        string: a string of either user or enemy to indicate who won
    """
    userStats = getStats(user_mon)
    enemyStats = getStats(enemy_mon)
    
    userAttack = getAttackPower(userStats, enemyStats)
    enemyAttack = getAttackPower(enemyStats, userStats)
    
    userTypes = getType(user_mon)
    enemyTypes = getType(enemy_mon)
    
    userTypingInfo = [getTypingInformation(pokemon_type) for pokemon_type in userTypes]
    enemyTypingInfo = [getTypingInformation(pokemon_type) for pokemon_type in enemyTypes]
    
    UserTypeMult = getBestDamageMultiplier(userTypingInfo, enemyTypingInfo)
    EnemyTypeMult = getBestDamageMultiplier(enemyTypingInfo, userTypingInfo)
    
    userSpeedMult = getSpeedMult(userStats['speed'], enemyStats['speed'])
    enemySpeedMult = getSpeedMult(enemyStats['speed'], userStats['speed'])
    
    userHp = userStats['hp']
    enemyHp = enemyStats['hp']
    userAttackPower = userAttack*UserTypeMult*userSpeedMult
    enemyAttackPower = enemyAttack*EnemyTypeMult*enemySpeedMult
    while(userHp > 0 and enemyHp > 0):
        userHp = userHp - enemyAttackPower
        enemyHp = enemyHp - userAttackPower
    if userHp > enemyHp:
        return 'User'
    if userHp < enemyHp:
        return 'Enemy'
    else:
        #Tiebreak with speed favoring user
        if userStats['speed'] >= enemyStats['speed']:
            return 'User'
        else:
            return 'Enemy'        
        
def getStats(pokemon):
    """Gets the stats of a pokemon

    Args:
        pokemon string: name of the user's pokemon

    Raises:
        Exception: if the stats can't be fetched from the endpoint

    Returns:
        dictionary dictionary of the pokemon stats
    """
    Resp = getPokemon(pokemon)
    if Resp.status_code != 200:
        raise Exception(f"Failed to get stats for {pokemon}: Status code {Resp.status_code}")
    Data = Resp.json()
    return {stat['stat']['name']: stat['base_stat'] for stat in Data['stats']}

def getAttackPower(attackerStats, defenderStats):
    """Calculate the attack power as the difference between the attacking pokemon's attack and the defenders defense or 
        the difference between special attack and special defense whichever is greater (min of 1)
        
    Args:
        attackerStats dictionary:  
        defenderStats dictionary: 

    Returns:
        Float representing the attack power of the relevant mon
    """
    attackDif = attackerStats['attack'] - defenderStats['defense']
    sattackDif = attackerStats['special-attack'] - defenderStats['special-defense']
    atkPower = max(attackDif, sattackDif)
    if atkPower < 0:
        atkPower = 1
    return atkPower

def getSpeedMult(attackerSpeed, defenderSpeed):
    """_summary_

    Args:
        attackerSpeed int: the attacker speed
        defenderSpeed int: the defender speed

    Returns:
        float: a modifier to be applied to attack power for the faster pokemon
    """
    if attackerSpeed > defenderSpeed:
        return 1.2
    else: 
        return 1.0

def getType(pokemon):
    """gets the type of a pokemon using the api endpoints

    Args:
        pokemon string: name of the pokemon

    Returns:
        a dictionary with the typing info
    """
    Resp = getPokemon(pokemon)
    Data = Resp.json()
    return {type_info['type']['name'] for type_info in Data['types']}

def getTypingInformation(type):
    """fetches typing matchup information with an api endpoint

    Args:
        type string: the name of the type we are fetching info for

    Returns:
        dictionary: a dictionary containing the matchup information
    """
    Resp = requests.get("https://pokeapi.co/api/v2/type/" + type + '/', stream=True, timeout=120)
    Data = Resp.json()
    type_name = Data.get('name', 'Unknown')
    damage_relations = Data.get('damage_relations', {})
    processed_relations = {}
    for key, value in damage_relations.items():      
        processed_relations[key] = [relation['name'] for relation in value]
    return {
        "type": type_name,
        "damage_relations": processed_relations
    }
    
def getBestDamageMultiplier(attackingTypesInfo, defendingTypesInfo):
    """Gets the best damage multiplier based on the attacker and defender typing

    Args:
        attackingTypesInfo  dictioary: dictionary containing the attacker typing info
        defendingTypesInfo dictionary: dictionary containing the defender typing info

    Returns:
        float: the best multiplier based on type matchups
    """
        
    #To account for pokemon being able to potentially learn moves not 
    #of their own type the penalties are not as harsh
    type_effectiveness = {
        "double_damage_to": 2.0,
        "half_damage_to": 0.75,
        "no_damage_to": 0.5
    }
    best_multiplier = 1.0
    for attacker_type_info in attackingTypesInfo:
        for defender_type_info in defendingTypesInfo:
            defender_type = defender_type_info["type"]
            damage_relations = attacker_type_info["damage_relations"]

            # Check damage relations for each defender's type
            for relation, multiplier in type_effectiveness.items():
                if defender_type in damage_relations.get(relation, []):
                    best_multiplier = max(best_multiplier, multiplier)

    return best_multiplier