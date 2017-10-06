# FLASK API
API for shopping list application

## Installation and setup

Clone this repo

https://github.com/MuthomiMate/Flask-Api.git
###### Navigate to the shoppinglist-api directory:

cd Flask-Api
###### Set Up environment Variables

source .env
###### Install dependencies:

pip install -r requirements.txt
###### Initialize, migrate and update the database:

python manage.py db init
python manage.py db migrate
python manage.py db upgrade
###### Test the application without coverage:

python manage.py test
###### Test the application with coverage:

nosetests --with-coverage --cover-package=tests && coverage report
###### Running application

To start application:

python run.py
## Access the endpoints 

Endpoints

|Resource URL|	Methods |	Description	|Requires Token
|------------|----------|---------------|--------------|
|/auth/register/|	POST	|User registers|	FALSE|
|/auth/login/	|POST	|User login	|FALSE
|/shoppinglists/|	POST|	Creates shopping list|	TRUE
|/shoppinglists/|	GET	|Get all shopping list|	TRUE
|/shoppinglists/int:id|	PUT	|Edit a shopping list|	TRUE
|/shoppinglists/int:id|	DELETE|	Delete a shopping list|	TRUE
|/shoppinglists/int:id|	GET	|Get a shopping list|	TRUE
|/shoppinglists/int:shoppinglist_id/items/|	POST|	Create a shoppinglist item|	TRUE
|/shoppinglists/int:shoppinglist_id/items/|	GET	|Get all shopping items in a shopping list|	TRUE
|/shoppinglists/shoppinglist_id/items/int:id| PUT|	Edit a shopping item|	TRUE
|/shoppinglists/shoppinglist_id/items/int:id|	DELETE|	Delete a shoppinglist item|	TRUE
|/shoppinglists/ishoppinglist_id/items/int:id|	GET| Get a single shoppinglist item|	TRUE
