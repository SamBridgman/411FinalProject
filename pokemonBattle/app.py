from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from pokemonBattle.getMon import getPokemon
from pokemonBattle.getMon import getRandomMon
from pokemonBattle.battle import PokemonBattle

app = Flask(__name__)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

#the user being stored
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    wins = db.Column(db.Integer, default=0)  

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
    username = session.get('username')
    if not username:
        flash("Please log in to access the dashboard.")
        return redirect(url_for('home'))

    # Retrieve user information from the database
    user = User.query.filter_by(username=username).first()
    if not user:
        flash("User not found.")
        return redirect(url_for('home'))

    return render_template('index.html', username=user.username, wins=user.wins)

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

    # Return battle result as JSON
    return jsonify({
        'winner': winner
    })


    
#LOGIN FORM LOGIC




#for registering users
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Handle JSON requests
        if request.content_type == "application/json":
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")
        else:  # Handle form submissions
            username = request.form.get("username")
            password = request.form.get("password")

        # Check if the username already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists")
            return redirect(url_for("signup"))

        # Hash the password and save the new user
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = User(username=username, password_hash=hashed_password, wins=0)  # Set wins to 0
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully!")
        return redirect(url_for("home"))

    # Render the signup page for GET requests
    return render_template("signup.html")


#for login
@app.route('/login', methods=['POST'])
def login():
    if request.content_type == "application/json":  # JSON request
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
    else:  # Form submission
        username = request.form.get('username')
        password = request.form.get('password')

    # Find the user in the database
    user = User.query.filter_by(username=username).first()

    # Check if user exists and password matches
    if user and bcrypt.check_password_hash(user.password_hash, password):
        session['username'] = username  # Save the username in the session
        flash("Login successful!")
        return redirect(url_for('dashboard'))

    flash("Invalid username or password")
    return redirect(url_for('home'))  # Redirect back to the login page

#for update password
@app.route('/update-password', methods=['POST'])
def update_password():
    # Handle JSON data
    if request.content_type == "application/json":
        data = request.get_json()
        username = data.get('username')
        new_password = data.get('new_password')
    else:  # Handle form data
        username = request.form.get('username')
        new_password = request.form.get('new_password')

    # Find the user in the database
    user = User.query.filter_by(username=username).first()

    if not user:
        if request.content_type == "application/json":
            return jsonify({'error': 'User not found'}), 404
        else:
            flash("User not found")
            return redirect(url_for('forgotpassword'))

    # Hash and update the new password
    user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    db.session.commit()

    # Redirect to the login page for form submissions
    if request.content_type == "application/json":
        return jsonify({'message': 'Password updated successfully. Please login again.'}), 200
    else:
        flash("Password updated successfully. Please login again.")
        return redirect(url_for('home'))  #back to login


#main
if __name__ == "__main__":
    app.secret_key = "your_secret_key"  # Required for flash messages
    app.run(debug=True, host="0.0.0.0", port=8080)  # Bind to all available interfaces
