#!/bin/bash

# Set the name of the virtual environment directory
VENV_DIR="pokemon_battle_venv"
REQUIREMENTS_FILE="requirements.lock"

# Determine the activate script path based on the platform
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
  ACTIVATE_SCRIPT="$VENV_DIR/Scripts/activate"  # Windows
else
  ACTIVATE_SCRIPT="$VENV_DIR/bin/activate"      # Unix/Linux
fi

# Check if the virtual environment already exists
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."
  python -m venv "$VENV_DIR"

  # Activate the virtual environment
  source "$ACTIVATE_SCRIPT"

  # Install dependencies from requirements.lock if it exists
  if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing dependencies from $REQUIREMENTS_FILE..."
    pip install --no-cache-dir -r "$REQUIREMENTS_FILE"
  else
    echo "Error: $REQUIREMENTS_FILE not found."
    exit 1
  fi
else
  source "$ACTIVATE_SCRIPT"
  echo "Virtual environment already exists. Activated."
fi