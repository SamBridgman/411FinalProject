from pokemonBattle.getMon import getPokemon
import requests

def PokemonBattle(user_mon, enemy_mon):
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
    Resp = getPokemon(pokemon)
    if Resp.status_code != 200:
        raise Exception(f"Failed to get stats for {pokemon}: Status code {Resp.status_code}")
    Data = Resp.json()
    return {stat['stat']['name']: stat['base_stat'] for stat in Data['stats']}

def getAttackPower(attackerStats, defenderStats):
    """Calculate the attack power as the difference between the attacking pokemon's attack and the defenders defense or 
        the difference between special attack and special defense whichever is greater (min of 1)
    """
    attackDif = attackerStats['attack'] - defenderStats['defense']
    sattackDif = attackerStats['special-attack'] - defenderStats['special-defense']
    atkPower = max(attackDif, sattackDif)
    if atkPower < 0:
        atkPower = 1
    return atkPower

def getSpeedMult(attackerSpeed, defenderSpeed):
    if attackerSpeed > defenderSpeed:
        return 1.2
    else: 
        return 1.0

def getType(pokemon):
    Resp = getPokemon(pokemon)
    Data = Resp.json()
    return {type_info['type']['name'] for type_info in Data['types']}

def getTypingInformation(type):
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