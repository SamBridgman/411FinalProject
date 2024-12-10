#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:8080"

# Enable JSON output display for debugging purposes
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

###############################################
#
# Health check
#
###############################################

# Check if the service is running
check_service() {
  echo "Checking service health..."
  response=$(curl -s -X GET "$BASE_URL/")
  if echo "$response" | grep -q "<title>Login"; then
    echo "Service is running and accessible."
  else
    echo "Failed to connect to the service."
    exit 1
  fi
}

###############################################
#
# User-related tests
#
###############################################

# Register a new user
register_user() {
  echo "Registering a new user..."
  response=$(curl -s -w "%{http_code}" -o /dev/null -X POST "$BASE_URL/register" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=testuser&password=testpassword")

  if [ "$response" -eq 302 ]; then
    echo "User registered successfully."
  else
    echo "Failed to register user. HTTP status code: $response"
    exit 1
  fi
}

# Login user
login_user() {
  echo "Logging in user..."
  response=$(curl -s -w "%{http_code}" -o /dev/null -X POST "$BASE_URL/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=testuser&password=testpassword")

  if [ "$response" -eq 302 ]; then
    echo "User logged in successfully (302 redirect)."
  else
    echo "Failed to log in user. HTTP status code: $response"
    exit 1
  fi
}

###############################################
#
# Pokemon-related tests
#
###############################################

# Get Pokémon stats
get_pokemon() {
  echo "Fetching Pokémon data (Pikachu)..."
  response=$(curl -s -X POST "$BASE_URL/get-pokemon" -d "pokemon=pikachu")
  if echo "$response" | grep -q '"pokemon_name": "Pikachu"'; then
    echo "Pokémon data fetched successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Response:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to fetch Pokémon data."
    exit 1
  fi
}

# Get enemy Pokémon
get_enemy_pokemon() {
  echo "Fetching enemy Pokémon..."
  response=$(curl -s -X POST "$BASE_URL/get-enemy-pokemon")
  if echo "$response" | grep -q '"enemy_pokemon_name"'; then
    echo "Enemy Pokémon fetched successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Response:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to fetch enemy Pokémon."
    exit 1
  fi
}

###############################################
#
# Battle tests
#
###############################################

Battle() {
  echo "Starting a battle..."
  battle_response=$(curl -c cookies.txt -b cookies.txt -s -X POST "$BASE_URL/start-battle" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "user_pokemon_name=pikachu&enemy_pokemon_name=bulbasaur")
  if echo "$battle_response" | grep -q '"winner"'; then
    echo "Battle completed successfully."
    echo "Battle Response: $battle_response"
  else
    echo "Failed to start the battle. Response: $battle_response"
    exit 1
  fi
}

###############################################
#
# Password management
#
###############################################

# Update user password
update_password() {
  echo "Updating user password..."
  response=$(curl -s -w "%{http_code}" -o /dev/null -c cookies.txt -b cookies.txt -X POST "$BASE_URL/update-password" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=testuser&new_password=newpassword")

  if [ "$response" -eq 302 ]; then
    echo "Password updated successfully (302 redirect)."
  else
    echo "Failed to update password. HTTP status code: $response"
    exit 1
  fi
}

###############################################
#
# Execute the smoketest
#
###############################################

echo "Starting smoketest for Pokemon Battle Simulator..."
check_service
register_user
login_user
get_pokemon
get_enemy_pokemon
battle
update_password
echo "Smoketest completed successfully!"