import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# db_drop_and_create_all()

DRINK_PER_PAGE = 10

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, True')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PATCH,PUT,DELETE, OPTIONS')

    return response

def drink_page(request, drinks, format_='short'):
    print('->> ENTER - ->>||')
    page = request.args.get('page', 1, type=int)
    start = (page -1) * DRINK_PER_PAGE
    end = start + DRINK_PER_PAGE
    if format_ == 'short':
        formatted_page = [drink.short() for drink in drinks]
    else:
        print('->> ENTER2 -->>||')
        formatted_page = [drink.long() for drink in drinks]
        print('->> DONE 11 -->>|')

    current_page = formatted_page[start:end]
    print('->> DONE -->>|')

    return current_page

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def getting_drinks():

    try:
        drinks = Drink.query.all()
        print(drinks," ]]")

        # if len(drinks) == 0:
        #     abort(404)

        current_page = drink_page(request, drinks)
        return jsonify({
            'success': True,
            'drinks': current_page
        }), 200
    except:
        abort(404)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def getting_drinks_detail(payload):
    print(payload)
    try:
        drinks_detail = Drink.query.all()

        if len(drinks_detail) == 0:
            abort(404)

        current_page = drink_page(request, drinks_detail, format_='long')

        return jsonify({
            'success': True,
            'drinks': current_page
            }), 200
    except:
        abort(401)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=["POST"])
@requires_auth('post:drinks')
def creating_new_drinks(payload):
    print(payload)
    body = request.get_json()
    title = body['title']

    try:
        drink = Drink(
            title=title,
            recipe=json.dumps(body['recipe']))

        drink.insert()

        return jsonify({
            'success': True,
            'drinks': drink.long()
            }), 200
    except:
        abort(404)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def editing_drinks_detail(payload, drink_id):
    body = request.get_json()
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        if drink is None:
            abort(404)

        if 'title' in body:
            drink.title = body['title']

        if 'recipe' in body:
            drink.recipe = json.dumps(body['recipe'])

        drink.update()

        return jsonify({
            'success': True,
            }), 200
    except:
        abort(404)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def deleting_drinks(payload, drink_id):

    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if drink is None:
        abort(404)

    drink.delete()

    return jsonify({
        'success': True,
        'delete': drink_id
        }), 200



# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(400)
def bad_request_error(error):

    return jsonify({
        'success': False,
        'error': 400,
        'message': 'bad request'
        }), 400

@app.errorhandler(401)
def unathorized_error(error):

    return jsonify({
        'success': False,
        'error': 401,
        'message': 'unauthorized'
        }), 401

@app.errorhandler(403)
def forbidden_error(error):

    return jsonify({
        'success': False,
        'error': 403,
        'message': 'forbidden'
        }), 403

@app.errorhandler(405)
def method_not_found(error):

    return jsonify({
        'success': False,
        'error': 405,
        'message': 'method not found'
        })

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def resource_not_found(error):

    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
        }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def handling_auth_error(error):

    if isinstance(error, AuthError):
        return jsonify({
            'success': False,
            'error': error.status_code,
            'message': error.error
            }), error.status_code

