import json
from flask_api import FlaskAPI, status
from flask_sqlalchemy import SQLAlchemy

from flask import request, jsonify, abort, make_response

# local import

from instance.config import app_config

# For password hashing
from flask_bcrypt import Bcrypt

# initialize db
db = SQLAlchemy()


def create_app(config_name):
    from app.models import Shoppinglist, User, Shoppinglistitems
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

                    # GET request
                    # initialize search query, limit and page_no
                    search_query = request.args.get("q")
                    limit = int(request.args.get('limit', 1))
                    page_no = int(request.args.get('page', 1))
                    results = []
                    if search_query:
                        search_results = Shoppinglist.query.filter(Shoppinglist.name.ilike(
                            '%' + search_query + '%')).filter_by(created_by=user_id).all()
                        if search_results:
                            for shoppinglist in search_results:
                                obj={
                                'id': shoppinglist.id,
                                'name': shoppinglist.name,
                                'date_created': shoppinglist.date_created,
                                'date_modified': shoppinglist.date_modified,
                                'created_by': shoppinglist.created_by
                                }
                                results.append(obj)
                            return make_response(jsonify(results)), 200

                        # search_results does not contain anything, status code=Not found
                        response = {
                            'message': "Shopping list name does not exist"
                        }
                        return make_response(jsonify(response)), 404
                    else:
                        shoppingliss = Shoppinglist.query.filter_by(created_by=user_id)
                        limit = int(request.args.get('limit', 2))
                        page = int(request.args.get('page', 1))
                        paginated_lists = Shoppinglist.query.filter_by(created_by=user_id).\
                        order_by(Shoppinglist.name.asc()).paginate(page, limit)
                        results=[]
                        if shoppingliss == '':
                            response = jsonify({
                                "message": "You do not have  any shopping list"
                            })
                            return make_response(response), 404
                        else:
                            for shoppinglist in paginated_lists.items:
                                obj={
                                'name': shoppinglist.name,
                                'date_created': shoppinglist.date_created,
                                'date_modified': shoppinglist.date_modified,
                                }
                                results.append(obj)
                            nextPage = 'None'
                            prevPage = 'None'
                            if paginated_lists.has_next:
                                next_page = '/shoppinglists/?limit={}&page={}'.format(
                                    str(limit),
                                    str(page_no + 1)
                                )
                            if paginated_lists.has_prev:
                                prev_page = '/shoppinglists/?limit={}&page={}'.format(
                                    str(limit),
                                    str(page_no - 1)
                                )
                            response = {
                                'shopping lists': results,
                                'previous page': prevPage,
                                'next page': nextPage
                            }
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
        # get the access token from the authorization header
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Get the user id related to this access token
            user_id = User.decode_token(access_token)

            if not isinstance(user_id, str):
                # If the id is not a string(error), we have a user id
                # Get the shoppinglist with the id specified from the URL (<int:id>)
                shoppinglist = Shoppinglist.query.filter_by(id=id).first()
                if not shoppinglist:
                    # There is no shoppinglist with this ID for this User, so
                    # Raise an HTTPException with a 404 not found status code
                    abort(404)

                if request.method == "DELETE":
                    # delete the shoppinglist using our delete method
                    shoppinglist.delete()
                    return {
                        "message": "shoppinglist {} deleted".format(shoppinglist.id)
                    }, 200

                elif request.method == 'PUT':
                    # Obtain the new name of the shoppinglist from the request data
                    name = str(request.data.get('name', ''))

                    shoppinglist.name = name
                    shoppinglist.save()

                    response = {
                        'id': shoppinglist.id,
                        'name': shoppinglist.name,
                        'date_created': shoppinglist.date_created,
                        'date_modified': shoppinglist.date_modified,
                        'created_by': shoppinglist.created_by
                    }
                    return make_response(jsonify(response)), 200
                else:
                    # Handle GET request, sending back the shoppinglist to the user
                    response = {
                        'id': shoppinglist.id,
                        'name': shoppinglist.name,
                        'date_created': shoppinglist.date_created,
                        'date_modified': shoppinglist.date_modified,
                        'created_by': shoppinglist.created_by
                    }
                    return make_response(jsonify(response)), 200
            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                # return an error response, telling the user he is Unauthorized
                return make_response(jsonify(response)), 401

    @app.route('/shoppinglists/<int:shoppinglist_id>/items/', methods=['POST', 'GET'])
    def shoppinglistsitems(shoppinglist_id):
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
                        shoppinglistitem = Shoppinglistitems(name=name, shoppinglistname=shoppinglist_id)
                        shoppinglistitem.save()
                        response = jsonify({
                            'id': shoppinglistitem.id,
                            'name': shoppinglistitem.name,
                            'date_created': shoppinglistitem.date_created,
                            'date_modified': shoppinglistitem.date_modified,
                            'shoppinglistname': shoppinglist_id
                        })

                        return make_response(response), 201

                else:
                    # GET all the shoppinglists created by this user

                    shoppinglistsitems = Shoppinglistitems.query.filter_by(shoppinglistname=shoppinglist_id)
                    results = []

                    for shoppinglistitem in shoppinglistsitems:
                        obj = {
                            'id': shoppinglistitem.id,
                            'name': shoppinglistitem.name,
                            'date_created': shoppinglistitem.date_created,
                            'date_modified': shoppinglistitem.date_modified,
                            'shoppinglistname': shoppinglist_id
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

    @app.route('/shoppinglists/<int:shoppinglist_id>/items/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def shoppinglistitem_manipulation(id, shoppinglist_id, **kwargs):
        # get the access token from the authorization header
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Get the user id related to this access token
            user_id = User.decode_token(access_token)

            if not isinstance(user_id, str):
                # If the id is not a string(error), we have a user id
                # Get the shoppinglist with the id specified from the URL (<int:id>)
                shoppinglistitems = Shoppinglistitems.query.filter_by(id=id).first()
                if not shoppinglistitems:
                    # There is no shoppinglist with this ID for this User, so
                    # Raise an HTTPException with a 404 not found status code
                    abort(404)

                if request.method == "DELETE":
                    # delete the shoppinglist using our delete method
                    shoppinglistitems.delete()
                    return {
                        "message": "item {} deleted".format(shoppinglistitems.id)
                    }, 200

                elif request.method == 'PUT':
                    # Obtain the new name of the shoppinglist from the request data
                    name = str(request.data.get('name', ''))

                    shoppinglistitems.name = name
                    shoppinglistitems.save()

                    response = {
                        'id': shoppinglistitems.id,
                        'name': shoppinglistitems.name,
                        'date_created': shoppinglistitems.date_created,
                        'date_modified': shoppinglistitems.date_modified,
                        'shoppinglistname': shoppinglistitems.shoppinglistname
                    }
                    return make_response(jsonify(response)), 200
                else:
                    # Handle GET request, sending back the shoppinglist to the user
                    response = {
                        'id': shoppinglistitems.id,
                        'name': shoppinglistitems.name,
                        'date_created': shoppinglistitems.date_created,
                        'date_modified': shoppinglistitems.date_modified,
                        'shoppinglistname': shoppinglistitems.shoppinglistname
                    }
                    return make_response(jsonify(response)), 200
            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                # return an error response, telling the user he is Unauthorized
                return make_response(jsonify(response)), 401

    # import the authentication blueprint and register it on the app
    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint)
    return app
