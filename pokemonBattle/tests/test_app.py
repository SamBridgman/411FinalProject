import pytest
from flask import url_for
from pokemonBattle.app import app, db, User, bcrypt
from flask_bcrypt import generate_password_hash

def setup_module(module):
    """Set up test database and app context."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_users.db'
    app.secret_key = "test_secret_key"  # Added secret key for tests
    with app.app_context():
        db.create_all()
        # Create a test user
        salt = "random_salt"  # Add a test salt
        hashed_password = generate_password_hash("testpassword" + salt).decode("utf-8")
        user = User(username="testuser", password_hash=hashed_password, salt=salt)  # Include the salt
        db.session.add(user)
        db.session.commit()

def teardown_module(module):
    """Clean up test database."""
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client():
    """Provide a test client for the Flask app."""
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test the home page (login page)."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_signup_page(client):
    """Test the signup page."""
    response = client.get('/signup')
    assert response.status_code == 200
    assert b'Sign Up' in response.data

def test_dashboard_access(client):
    """Test access to the dashboard without logging in."""
    response = client.get('/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert b'Please log in to access the dashboard' in response.data

def test_register_user(client):
    """Test user registration."""
    response = client.post('/register', data={
        'username': 'newuser',
        'password': 'newpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Account created successfully!' in response.data

def test_login_user(client):
    """Test user login."""
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'testuser' in response.data  # Check for username in the dashboard

def test_invalid_login(client):
    """Test login with invalid credentials."""
    response = client.post('/login', data={
        'username': 'wronguser',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data

def test_update_password(client):
    """Test updating the password for an existing user."""
    response = client.post('/update-password', data={
        'username': 'testuser',
        'new_password': 'updatedpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Password updated successfully' in response.data
    # Verify login with the new password
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        salt = user.salt
        assert bcrypt.check_password_hash(user.password_hash, 'updatedpassword' + salt)

def test_get_pokemon(client, monkeypatch):
    """Test fetching a Pokémon by name."""
    def mock_get_pokemon(name):
        class MockResponse:
            status_code = 200
            def json(self):
                return {
                    'name': 'pikachu',
                    'stats': [
                        {'stat': {'name': 'speed'}, 'base_stat': 90},
                        {'stat': {'name': 'attack'}, 'base_stat': 55}
                    ],
                    'sprites': {'front_default': 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png'}
                }
        return MockResponse()

    monkeypatch.setattr('pokemonBattle.getMon.getPokemon', mock_get_pokemon)

    response = client.post('/get-pokemon', data={'pokemon': 'pikachu'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['pokemon_name'] == 'Pikachu'
    assert data['pokemon_stats']['speed'] == 90
    assert data['pokemon_sprite'] == 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png'