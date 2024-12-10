Application overview: 

Our application is a pokemon battle simulator\! Each user can create an account and log in, and their account will store their wins from the battle simulator. Within the application, once you log in, the functionality of the battle simulator is simple. You can choose the pokemon which you would like to battle with by typing in its name and clicking the ‘Get Pokémon’ button. This will pull up your pokemon’s stats and spite (if it exists), then you can click the ‘Generate Enemy Pokémon’ button to generate a random enemy pokemon, which will also display its stats and sprite\! Finally you can click the ‘Start Battle’ function and the winner will be displayed. If the winner was your pokemon, you will see that your displayed wins will be incremented by one.

Route Descriptions:

Route: /  
Request type: GET  
Purpose: Render the login page  
Request Body: None  
Response Format: HTML  
Example Request: N/A  
Example Response: Renders the login page with status 200

Route: /signup  
	Request type: GET   
	Purpose: Render the signup page  
	Request Body: None  
	Response Format: HTML  
	Example Request: N/A  
	Example Response: Renders the signup page with status 200

Route: /index  
	Request type: GET   
	Purpose: Render the index page  
	Request Body: None  
	Response Format: HTML  
	Example Request: N/A  
	Example Response: Renders the index page with status 200

Route: /update-password  
	Request type: GET  
	Purpose: Render the forgot password page  
	Request Body: None  
	Response Format: HTML  
	Example Request: N/A  
	Example Response: Renders the forgot password pager with status 200

Route: /dashboard  
	Request type: GET   
	Purpose: Render the dashboard for logged in users  
	Request Body: None  
	Response Format: HTML  
	Example Request: N/A  
	Example Response: Displays the dashboard (if successful)

Route: /get-pokemon  
	Request type: POST  
	Purpose: Read the entered pokemon name and make an api request, then display the fetched pokemon if it exists  
	Request Body: pokemon (String): the name of the pokemon to fetch  
	Response Format: JSON  
	Example Request: { “pokemon”: “charmander” }  
	Example Response: {“pokemon\_name”: “charmander”, “pokemon\_stats”: { “speed”: num, “attack”: num (etc) }, “pokemon\_sprite”: “https://spriteurl” }

Route: /get-enemy-pokemon  
	Request type: POST  
	Purpose: Fetch a random enemy pokemon from the pokemon api and display the fetched pokemon  
	Request Body: None  
	Response Format: JSON  
	Example Request: N/A   
	Example Response: {“pokemon\_name”: “charizard”, “pokemon\_stats”: { “speed”: num, “attack”: num (etc) }, “pokemon\_sprite”: “https://spriteurl” }

Route: /start-battle  
	Request type: POST  
	Purpose: Start the battle function and display the winner  
	Request Body: user\_pokemon\_name (String): The user’s Pokemon name, enemy\_pokemon\_name (String): The enemy Pokemon name  
	Response Format: JSON  
	Example Request: {"user\_pokemon\_name": "pikachu",  "enemy\_pokemon\_name": "charizard" }  
	Example Response: { "winner": "User", "wins": 5 }

Route: /register  
	Request type: GET, POST  
	Purpose: Register a new user account   
	Request Body: username (String): The user’s username, password (String): The user’s password  
	Response Format: JSON or Redirect  
	Example Request: { "username": "newuser123", "password": "securepassword"}  
	Example Response: Renders signup page  

Route: /Login  
	Request type: POST   
	Purpose: Login the user  
	Request Body: username (String): The user’s username, password (String): The user’s password  
	Response Format: JSON or Redirect  
	Example Request: { "username": "newuser123", "password": "securepassword"}  
	Example Response: Successfully signs the user in

Route: /update-password  
	Request type: POST  
	Purpose: Update a user’s password  
	Request Body: username (String): The user’s username, password (String): The user’s password  
	Response Format: JSON   
	Example Request: {"username": "user123", "new\_password": "newsecurepassword"}  
	Example Response: Redirects to the login page  
