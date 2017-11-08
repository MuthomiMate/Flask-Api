# app/ --init__.py
import json
import re
import random
import string
from flask_api import FlaskAPI, status
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

from flask import request, jsonify, abort, make_response, redirect

# local import

from instance.config import app_config

# For password hashing
from flask_bcrypt import Bcrypt

# initialize db
db = SQLAlchemy() # pylint: disable=invalid-name


def create_app(config_name):
    """ creates the app according to config name specified """
    from app.models import Shoppinglist, User, Shoppinglistitems
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    db.init_app(app)

    @app.route('/', methods=[ 'GET'])
    def index():

        return redirect("http://docs.shoppinglistapi7.apiary.io")

    @app.errorhandler(404)
    def not_found(error):
        """ handles error when users enters inappropriate endpoint """
        response = {
            'message' : 'Page not found'
        }
        return make_response(jsonify(response)), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        """ handles errors if users uses method that is not allowed in an endpoint """
        response = {
            'message' : 'Method not allowed'
        }
        return make_response(jsonify(response)), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        """ handles internal server error reponses """
        response = {
            'message' : 'Internal Server Error'
        }
        return make_response(jsonify(response)), 500
    @app.errorhandler(400)
    def bad_request(error):
        """ handles error when users enters inappropriate endpoint """
        response = {
            'message' : 'Bad Request'
        }
        return make_response(jsonify(response)), 400
    @app.route('/shoppinglists/', methods=['POST', 'GET'])
    def shoppinglists():
        """ Get the access token from the header """
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
         # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                # Go ahead and handle the request, the user is authenticated

                if request.method == "POST":
                    name = str(request.data.get('name', ''))
                    shoppinglistexist = Shoppinglist.query.filter_by(name=request.data['name'], created_by=user_id).first()
                    if name == '':
                        response = {
                            'message' : 'Enter name'
                        }
                        return make_response(jsonify(response))

                    if name:
                        if re.match("[a-zA-Z0-9- .]+$", name):
                            if not shoppinglistexist:
                                shoppinglist = Shoppinglist(name=name, created_by=user_id)
                                shoppinglist.save()
                                response = jsonify({
                                    'id': shoppinglist.id,
                                    'name': shoppinglist.name,
                                    'date_created': shoppinglist.date_created,
                                    'date_modified': shoppinglist.date_modified
                                })

                                return make_response(response), 201
                            else:
                                response = {
                                    'message' : 'That shopping list exists'
                                }
                                return make_response(jsonify(response))
                        else:
                            response = {
                                'message' : 'Name should not contain special characters'
                            }
                            return make_response(jsonify(response))

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
                                obj = {
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
                        return make_response(jsonify(response))
                    else:
                        shoppingliss = Shoppinglist.query.filter_by(created_by=user_id).all()
                        if not shoppingliss:
                            response = jsonify({
                                "message": "You do not have  any shopping list"
                            })
                            return make_response(response)
                        limit = int(request.args.get('limit', 10))
                        page = int(request.args.get('page', 1))
                        paginated_lists = Shoppinglist.query.filter_by(created_by=user_id).\
                        order_by(Shoppinglist.name.asc()).paginate(page, limit)
                        results = []
                        if shoppingliss:
                            for shoppinglist in paginated_lists.items:
                                obj = {
                                    'name': shoppinglist.name,
                                    'date_created': shoppinglist.date_created,
                                    'date_modified': shoppinglist.date_modified,
                                    'id': shoppinglist.id,
                                }
                                results.append(obj)
                            next_page = 'None'
                            prev_page = 'None'
                            if paginated_lists.has_next:
                                next_page = '?limit={}&page={}'.format(
                                    str(limit),
                                    str(page_no + 1)
                                )
                            if paginated_lists.has_prev:
                                prev_page = '?limit={}&page={}'.format(
                                    str(limit),
                                    str(page_no - 1)
                                )
                            response = {
                                'shopping_lists': results,
                                'previous_page': prev_page,
                                'next_page': next_page
                            }
                            return make_response(jsonify(response)), 200

            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401
    @app.route('/shoppinglists/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def shoppinglist_manipulation(id):
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
                    response = {
                        'message' : 'That shoppinglists does not exist'
                    }
                    return make_response(jsonify(response))
                shoppinglistowner = Shoppinglist.query.filter_by(id=id, created_by=user_id).first()
                if not shoppinglistowner:
                    response = {
                        'message' : 'You do not have permission to view that shoppinglist'
                    }
                    return make_response(jsonify(response))

                if request.method == "DELETE":
                    # delete the shoppinglist using our delete method
                    shoppinglist.delete()
                    response = {
                        "message": "shoppinglist {} deleted".format(shoppinglist.id)
                    }
                    return make_response(jsonify(response)), 200

                elif request.method == 'PUT':
                    # Obtain the new name of the shoppinglist from the request data
                    name = str(request.data.get('name', ''))
                    if name == '':
                        response = {
                            'message' : 'Name cannot be empty'
                        }
                        return make_response(jsonify(response))
                    if re.match("[a-zA-Z0-9- .]+$", name):
                        shoppinglistexist = Shoppinglist.query.filter_by(name=request.data['name'], created_by=user_id).first()
                        if not shoppinglistexist:
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
                            response= {
                                'message' : 'Shoppinglist with that name exists'
                            }
                            return make_response(jsonify(response))
                    else:
                        response = {
                            'message' : 'Name should not have special characters'
                        }
                        return make_response(jsonify(response))
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

                shoppinglist = Shoppinglist.query.filter_by(id=shoppinglist_id).first()
                if not shoppinglist:
                    response = {
                        'message' : 'That shopping list does not exist'
                    }
                    return make_response(jsonify(response))
                shoppinglist = Shoppinglist.query.filter_by(id=shoppinglist_id, created_by=user_id).first()
                if not shoppinglist:
                    response = {
                        'message' : 'You do not have permission to view that shoppinglist'
                    }
                    return make_response(jsonify(response))

                if request.method == "POST":
                    name = str(request.data.get('name', ''))
                    if name == '':
                        response = {
                            'message' : 'Item name cannot be empty'
                        }
                        return make_response(jsonify(response))

                    if name:
                        if re.match("[a-zA-Z0-9- .]+$", name):
                            shoppinglistitemexist = Shoppinglistitems.query.filter_by(name=request.data['name'],
                                                                                shoppinglistid=shoppinglist_id).first()
                            if not shoppinglistitemexist:
                                shoppinglistitem = Shoppinglistitems(name=name,
                                                                    shoppinglistid=shoppinglist_id)
                                shoppinglistitem.save()
                                response = jsonify({
                                    'id': shoppinglistitem.id,
                                    'name': shoppinglistitem.name,
                                    'date_created': shoppinglistitem.date_created,
                                    'date_modified': shoppinglistitem.date_modified,
                                    'shoppinglistid': shoppinglist_id
                                })

                                return make_response(response), 201
                            else:
                                response = {
                                    'message' : 'shopping item exists'
                                }
                                return make_response(jsonify(response))
                        else:
                            response = {
                                'message' : 'Name cannot have special characters'
                            }
                            return make_response(jsonify(response))

                else:
                    # GET all the shoppingitems in this shopinglist created by this user

                    shoppinglistsitemss = Shoppinglistitems.query.filter_by(shoppinglistid=
                                                                            shoppinglist_id). all()
                    if not shoppinglistsitemss:
                        response = {
                            'message' : 'No items in this shopping list'
                        }
                        return make_response(jsonify(response))
                    results = []

                    for shoppinglistitem in shoppinglistsitemss:
                        obj = {
                            'id': shoppinglistitem.id,
                            'name': shoppinglistitem.name,
                            'date_created': shoppinglistitem.date_created,
                            'date_modified': shoppinglistitem.date_modified,
                            'shoppinglistid': shoppinglist_id
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

    @app.route('/shoppinglists/items/<int:id>',
               methods=['GET', 'PUT', 'DELETE'])
    def shoppinglistitem_manipulation(id):
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
                    # There is no shoppinglistitem with this ID for this User
                    response = {
                        'message': 'That item does not exist'
                    }
                    return make_response(jsonify(response))

                shoppinglist_idf = Shoppinglistitems.query.filter_by(id=id).first()
                shoppinglist_id=shoppinglist_idf.shoppinglistid
                shoppinglist = Shoppinglist.query.filter_by(id=shoppinglist_id).first()
                #check if the shopping_list belongs to that person
                shoppinglist = Shoppinglist.query.filter_by(id=shoppinglist_id, created_by=user_id).first()
                if not shoppinglist:
                    response = {
                        'message' : 'You do not have permission to view the items'
                    }
                    return make_response(jsonify(response))
                

                if request.method == "DELETE":
                    # delete the shoppingitem using our delete method
                    shoppinglistitems.delete()
                    return {
                        "message": "item {} deleted".format(shoppinglistitems.id)
                    }, 200

                elif request.method == 'PUT':
                    # Obtain the new name of the shoppingitem from the request data
                    name = str(request.data.get('name', ''))
                    if name == '':
                        response = {
                            'message' : 'Name cannot be empty'
                        }
                        return make_response(jsonify(response))
                    if re.match("[a-zA-Z0-9- .]+$", name):
                        shoppinglistitemexist = Shoppinglistitems.query.filter_by(name=request.data['name'],
                                                                                shoppinglistid=shoppinglist_id).first()
                        if not shoppinglistitemexist:
                            shoppinglistitems.name = name
                            shoppinglistitems.save()

                            response = {
                                'id': shoppinglistitems.id,
                                'name': shoppinglistitems.name,
                                'date_created': shoppinglistitems.date_created,
                                'date_modified': shoppinglistitems.date_modified,
                                'shoppinglistid': shoppinglistitems.shoppinglistid
                            }
                            return make_response(jsonify(response)), 200
                        else:
                            response = {
                                'message' : 'shopping item with that name exist'
                            }
                            return make_response(jsonify(response))
                    else:
                        response = {
                            'message' : 'name should not contain special characters'
                        }
                        return make_response(jsonify(response))
                else:
                    # Handle GET request, sending back the shoppinglist item to the user
                    response = {
                        'id': shoppinglistitems.id,
                        'name': shoppinglistitems.name,
                        'date_created': shoppinglistitems.date_created,
                        'date_modified': shoppinglistitems.date_modified,
                        'shoppinglistid': shoppinglistitems.shoppinglistid
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
    @app.route('/auth/ccpas',
               methods=['PUT'])
    def change_password():
         # get the access token from the authorization header
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Get the user id related to this access token
            user_id = User.decode_token(access_token)

            if not isinstance(user_id, str):
                # If the id is not a string(error), we have a user id
                if request.method == "PUT":
                    old_password = str(request.data.get('old_password', ''))
                    new_password = str(request.data.get('new_password', ''))

                    if old_password == '' or new_password == '':
                        response = {
                            'mesage' : 'please enter old and new password'
                        }
                        return make_response(jsonify(response))
                    else:

                        user = User.query.filter_by(id=user_id).first()
                        
                        if user:
                            if Bcrypt().check_password_hash(user.password, old_password):
                                encrypted_password = Bcrypt().generate_password_hash(new_password).decode()
                                user.password = encrypted_password
                                user.save()
                                response = {
                                    'message' : 'password changed sucessfully. Please login again'
                                }
                                return make_response(jsonify(response))
                            else:
                                response = { 
                                    'message' : 'password entered is incorrect. Try again!'
                                }
                                return make_response(jsonify(response))

            else: 
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                # return an error response, telling the user he is Unauthorized
                return make_response(jsonify(response)), 401

    @app.route('/auth/passreset',
               methods=['PUT'])
    def reset_password():
        email = str(request.data.get('email', ''))
        if not email:
            response = {
                'message' : 'Please enter email address'
            }
            return make_response(jsonify(response))
        else:
            user = User.query.filter_by(email=email).first()
            gen_password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            if user:
                #user with that email exists
                encrypted_password = Bcrypt().generate_password_hash(gen_password).decode()
                user.password = encrypted_password
                user.save()
                response = {
                    'message' : 'You password is '+ str(gen_password) + '. Please change the password after login'
                }
                return make_response(jsonify(response))

            else:
                response = {
                    'message' : 'user not registered. Please register'
                }
                return make_response(jsonify(response))


    # import the authentication blueprint and register it on the app
    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint)
    return app
