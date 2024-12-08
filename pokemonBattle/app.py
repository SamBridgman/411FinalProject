from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import logging
import os
from getMon import *
from battle import *

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


app = Flask(__name__)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):

    """
    A database model representing a user.

    Attributes:
        id (int): The primary key for the user.
        username (str): The unique username of the user.
        password_hash (str): The hashed password for the user.
        wins (int): The number of wins the user has, defaults to 0.
        salt (str): The unique salt used for hashing the user's password.

    Methods:
        __repr__: Returns a string representation of the user instance, showing the username.
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    wins = db.Column(db.Integer, default=0)  
    salt = db.Column(db.String(200))

    def __repr__(self):
        return f"<User {self.username}>"


#TO SERVE THE FRONT END

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/update-password')
def forgotpassword():
    return render_template('forgotpassword.html')

@app.route('/dashboard')
def dashboard():
    """
    Display the user dashboard if the user is logged in.

    Raises:
        Exception: If the user is not logged in or not found in the database.

    Returns:
        Template/Redirect:
            - If the user is logged in:
                - Renders the dashboard template with the user's details (username and win count).
            - If the user is not logged in:
                - Redirects to the home page with a message prompting the user to log in.
            - If the user is not found in the database:
                - Redirects to the home page with an error message.
    """
    try:
        logging.info("GET request received on /dashboard route.")

        username = session.get('username')
        if not username:
            logging.warning("Access denied to dashboard: No user logged in.")
            flash("Please log in to access the dashboard.")
            return redirect(url_for('home'))

        logging.info(f"Dashboard access attempt by user: {username}")

        user = User.query.filter_by(username=username).first()
        if not user:
            logging.error(f"User '{username}' not found in the database.")
            flash("User not found.")
            return redirect(url_for('home'))

        logging.info(f"Dashboard successfully rendered for user: {username}")
        return render_template('index.html', username=user.username, wins=user.wins)
    except Exception as e:
        logging.error(f"An error occurred while accessing the dashboard: {e}")
        flash("An error occurred. Please try again.")
        return redirect(url_for('home'))

@app.route('/get-pokemon', methods=['POST'])
def get_pokemon():
    pokemon_name = request.form.get('pokemon')  
    if not pokemon_name:
        return jsonify({'error': 'Please enter a Pokémon name.'}), 400

    # Fetch Pokémon data using the `getStats` function
    response = getPokemon(pokemon_name.lower())  
    if response.status_code != 200:
        flash("Pokémon not found. Please try again.")
        return redirect(url_for('dashboard'))

    # Decode and unpack the JSON response
    data = response.json()
    pokemon_stats = {stat['stat']['name']: stat['base_stat'] for stat in data['stats']}
    pokemon_sprite = data['sprites']['front_default']

    # Pass data to the template for rendering
    return jsonify({
        'pokemon_name': data['name'].capitalize(),
        'pokemon_stats': pokemon_stats,
        'pokemon_sprite': pokemon_sprite
    })

@app.route('/get-enemy-pokemon', methods=['POST'])
def get_enemy_pokemon():
    # Fetch random Pokémon data
    response = getRandomMon()  
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch an enemy Pokémon. Please try again.'}), 500

    # Decode and unpack the JSON response
    data = response.json()
    enemy_pokemon_name = data['name'].capitalize()
    enemy_pokemon_stats = {stat['stat']['name']: stat['base_stat'] for stat in data['stats']}
    enemy_pokemon_sprite = data['sprites']['front_default']

    # Return data as JSON
    return jsonify({
        'enemy_pokemon_name': enemy_pokemon_name,
        'enemy_pokemon_stats': enemy_pokemon_stats,
        'enemy_pokemon_sprite': enemy_pokemon_sprite
    })


@app.route('/start-battle', methods=['POST'])
def start_battle():
    # Retrieve Pokémon names from the frontend
    user_pokemon_name = request.form.get('user_pokemon_name')
    enemy_pokemon_name = request.form.get('enemy_pokemon_name')

    # Perform a basic check to ensure both Pokémon are provided
    if not user_pokemon_name or not enemy_pokemon_name:
        return jsonify({'error': 'Both Pokémon must be selected to start a battle.'}), 400

    # Fetch Pokémon data using the provided names
    winner = PokemonBattle(user_pokemon_name, enemy_pokemon_name)
    username= session.get('username')
    user = User.query.filter_by(username=username).first()
    
    if winner == 'User':
        user.wins = user.wins + 1
    db.session.commit()

    # Return battle result as JSON
    return jsonify({
        'winner': winner,
        'wins': user.wins
    })


    
#LOGIN FORM LOGIC




@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Fetch information about a Pokémon from the API.

    Args:
        pokemon (str): The name of the Pokémon to get data for.

    Raises:
        Exception: If there is an error with the API response (e.g., the Pokémon is not found).

    Returns:
        dict: The response data from the API containing information about the Pokémon.
        Html Template
    """
    try:
        if request.method == "POST":
            logging.info("POST request received on /register route.")

            if request.content_type == "application/json":
                logging.info("Request content type is JSON.")
                data = request.get_json()
                username = data.get("username")
                password = data.get("password")
            else:
                logging.info("Request content type is form-data.")
                username = request.form.get("username")
                password = request.form.get("password")

            logging.info(f"Attempting to register user: {username}")

            if User.query.filter_by(username=username).first():
                logging.warning(f"Username '{username}' already exists.")
                flash("Username already exists")
                return redirect(url_for("signup"))

            salt = str(os.urandom(16))
            logging.debug(f"Generated salt for user '{username}'.")

            hashed_password = bcrypt.generate_password_hash(password + salt).decode("utf-8")
            logging.debug(f"Password hashed for user '{username}'.")

            new_user = User(username=username, password_hash=hashed_password, wins=0, salt=salt)
            db.session.add(new_user)
            db.session.commit()

            logging.info(f"User '{username}' registered successfully.")
            flash("Account created successfully!")
            return redirect(url_for("home"))
    except Exception as e:
        logging.error(f"An error occurred during registration: {e}")
        flash("An error occurred. Please try again.")
        return redirect(url_for("signup"))

    logging.info("GET request received on /register route.")
    return render_template("signup.html")


#for login
@app.route('/login', methods=['POST'])
def login():
    """
    Handle user login by verifying credentials.

    Raises:
        Exception: If the user does not exist in the database or the password is invalid.

    Returns:
        Redirect: Redirects to the dashboard if login is successful.
        Redirect: Redirects to the home page with an error message if login fails.
    """
    try:
        logging.info("POST request received on /login route.")

        if request.content_type == "application/json":
            logging.info("Request content type is JSON.")
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
        else:
            logging.info("Request content type is form-data.")
            username = request.form.get('username')
            password = request.form.get('password')

        logging.info(f"Attempting to log in user: {username}")

        user = User.query.filter_by(username=username).first()

        if not user:
            logging.warning(f"Login attempt failed for username '{username}': User not found.")
            flash("Invalid username or password")
            return redirect(url_for('home'))

        salt = user.salt
        logging.debug(f"Salt retrieved for username '{username}'.")

        salted_password = password + salt
        if bcrypt.check_password_hash(user.password_hash, salted_password):
            session['username'] = username
            logging.info(f"User '{username}' logged in successfully.")
            flash("Login successful!")
            return redirect(url_for('dashboard'))

        logging.warning(f"Login attempt failed for username '{username}': Invalid password.")
        flash("Invalid username or password")
        return redirect(url_for('home'))

    except Exception as e:
        logging.error(f"An error occurred during login: {e}")
        flash("An error occurred. Please try again.")
        return redirect(url_for('home'))

@app.route('/update-password', methods=['POST'])
def update_password():
    """
    Update the user's password in the database.

    Raises:
        Exception: If the user is not found in the database.

    Returns:
        dict/Redirect:
            - If the request is JSON:
                - Returns a JSON response indicating success or an error with the appropriate HTTP status code.
            - If the request is a form submission:
                - Redirects to the login page with a success message on successful password update.
                - Redirects to the forgot password page with an error message if the user is not found.
    """
    try:
        logging.info("POST request received on /update-password route.")

        if request.content_type == "application/json":
            logging.info("Request content type is JSON.")
            data = request.get_json()
            username = data.get('username')
            new_password = data.get('new_password')
        else:
            logging.info("Request content type is form-data.")
            username = request.form.get('username')
            new_password = request.form.get('new_password')

        logging.info(f"Password update attempt for user: {username}")

        user = User.query.filter_by(username=username).first()

        if not user:
            logging.warning(f"Password update failed for username '{username}': User not found.")
            if request.content_type == "application/json":
                return jsonify({'error': 'User not found'}), 404
            else:
                flash("User not found")
                return redirect(url_for('forgotpassword'))

        salt = user.salt
        logging.debug(f"Salt retrieved for username '{username}'.")

        salted_password = new_password + salt
        hashed_password = bcrypt.generate_password_hash(salted_password).decode('utf-8')
        logging.debug(f"Password hashed for user '{username}'.")

        user.password_hash = hashed_password
        db.session.commit()

        logging.info(f"Password updated successfully for user '{username}'.")

        if request.content_type == "application/json":
            return jsonify({'message': 'Password updated successfully'}), 200
        else:
            flash("Password updated successfully! Please log in.")
            return redirect(url_for('home'))
    except Exception as e:
        logging.error(f"An error occurred during password update: {e}")
        if request.content_type == "application/json":
            return jsonify({'error': 'An internal error occurred'}), 500
        else:
            flash("An error occurred. Please try again.")
            return redirect(url_for('forgotpassword'))

#main
if __name__ == "__main__":
    app.secret_key = "your_secret_key"  
    app.run(debug=True, host="0.0.0.0", port=8080) 
