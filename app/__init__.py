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
		if request.method == "POST":
			name = str(request.data.get('name', ''))
			if name:
				shoppinglist = Shoppinglist(name=name)
				shoppinglist.save()
				response = jsonify({
					'id': shoppinglist.id,
					'name': shoppinglist.name,
					'date_created': shoppinglist.date_created,
					'date_modified': shoppinglist.date_modified
				})
				response.status_code = 201
				return response
		else:
			shoppinglists = Shoppinglist.get_all()
			results = []
			for shoppinglist in shoppinglists:
				obj = {
					'id': shoppinglist.id,
					'name': shoppinglist.name,
					'date_created': shoppinglist.date_created,
					'date_modified': shoppinglist.date_modified
				}
				results.append(obj)
			response = jsonify(results)
			response.status_code = 200
			return response
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