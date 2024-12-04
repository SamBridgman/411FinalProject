from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

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
