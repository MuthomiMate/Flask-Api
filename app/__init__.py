from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy

# local import
from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()

from flask import request, jsonify, abort
def create_app(config_name):
	from app.models import Shoppinglist
	app = FlaskAPI(__name__, instance_relative_config=True)
	app.config.from_object(app_config['development'])
	app.config.from_pyfile('config.py')
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
	db.init_app(app)

	@app.route('/shoppinglists/', methods=['POST', 'GET'])
    def shoppinglists():
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
         # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                # Go ahead and handle the request, the user is authenticated

                if request.method == "POST":
                    name = str(request.data.get('name', ''))
                    if name:
                        shoppinglist = Shoppinglist(name=name, created_by=user_id)
                        shoppinglist.save()
                        response = jsonify({
                            'id': shoppinglist.id,
                            'name': shoppinglist.name,
                            'date_created': shoppinglist.date_created,
                            'date_modified': shoppinglist.date_modified,
                            'created_by': user_id
                        })

                        return make_response(response), 201

                else:
                    # GET all the shoppinglists created by this user
                    shoppinglists = Shoppinglist.query.filter_by(created_by=user_id)
                    results = []

                    for shoppinglist in shoppinglists:
                        obj = {
                            'id': shoppinglist.id,
                            'name': shoppinglist.name,
                            'date_created': shoppinglist.date_created,
                            'date_modified': shoppinglist.date_modified,
                            'created_by': shoppinglist.created_by
                        }
                        results.append(obj)

                    return make_response(jsonify(results)), 200
            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401
	@app.route('/shoppinglists/<int:id>', methods=['GET', 'PUT', 'DELETE'])
	def shoppinglist_manipulation(id, **kwargs):
		# retrieve a buckelist using it's ID
		shoppinglist = Shoppinglist.query.filter_by(id=id).first()
		if not shoppinglist:
			# Raise an HTTPException with a 404 not found status code
			abort(404)
		if request.method == 'DELETE':
			shoppinglist.delete()
			return {
			"message": "shoppinglist {} deleted successfully".format(shoppinglist.id)
			}, 200
		elif request.method == 'PUT':
			name = str(request.data.get('name', ''))
			shoppinglist.name = name
			shoppinglist.save()
			response = jsonify({
				'id': shoppinglist.id,
				'name': shoppinglist.name,
				'date_created': shoppinglist.date_created,
				'date_modified': shoppinglist.date_modified
			})
			response.status_code = 200
			return response
		else:
			 # GET
			 response = jsonify({
			 	'id': shoppinglist.id,
			 	'name': shoppinglist.name,
			 	'date_created': shoppinglist.date_created,
			 	'date_modified': shoppinglist.date_modified
			 })
			 response.status_code = 200
			 return response
	# import the authentication blueprint and register it on the app
	from .auth import auth_blueprint
	app.register_blueprint(auth_blueprint)
	return app