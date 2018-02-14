import re

from flask import request

from api.bucketlists.serializers import api, email_and_password
from flask_restplus import Resource
from models.models import User

ns = api.namespace('auth', description='User authentication')


@ns.route('/register')
@api.response(400, 'Your email is invalid. Please enter a valid email.')
@api.response(400, 'Your password should contain at least one number, \
one lowercase, one uppercase letter and at least six characters')
@api.response(201, 'You registered successfully. Please log in.')
@api.response(409, 'User already exists. Please log in.')
class Registration(Resource):
    """This is where we register a new user."""

    @api.expect(email_and_password)
    def post(self):
        """Handle POST request at /auth/register."""
        post_data = request.json
        email = post_data.get('email')
        password = post_data.get('password')

        if not email_is_valid(email):
            response = {
                'message': 'Your email is invalid. Please enter a valid email.'
            }
            return response, 400

        elif not password_is_valid(password):
            response = {
                'message': 'Your password should contain at least one number, \
one lowercase, one uppercase letter and at least six characters'
            }
            return response, 400

        else:
            # Query to see if the user already exists
            user = User.query.filter_by(email=email).first()

            if not user:
                # There is no user so we'll try to register them
                try:
                    user = User(email=email, password=password)
                    user.save()

                    response = {
                        'message':
                        'You registered successfully. Please log in.'
                    }
                    return response, 201

                except Exception as e:
                    response = {
                        'message': str(e)
                    }
                    return response, 401
            else:
                # There is an existing user.
                response = {
                    'message': 'User already exists. Please login.'
                }
                return response, 409


@ns.route('/login')
@api.response(200, 'You logged in successfully.')
@api.response(401, 'Invalid email or password. Please try again.')
class Login(Resource):
    """This handles user login and access token generation."""

    @api.expect(email_and_password)
    def post(self):
        """Handle POST request for /auth/login."""
        post_data = request.json
        email = post_data.get('email')
        password = post_data.get('password')

        try:
            # Get the user object using their email (unique to every user)
            user = User.query.filter_by(email=email).first()

            # Try to authenticate the found user using their password
            if user and user.is_registered_password(password):
                # Generate the access token.
                access_token = user.generate_token(user.id)
                if access_token:
                    response = {
                        'message': 'You logged in successfully.',
                        'access_token': access_token.decode()
                    }
                    return response, 200
            else:
                # User does not exist. Therefore, we return an error message
                response = {
                    'message': 'Invalid email or password. Please try again'
                }
                return response, 401

        except Exception as e:
            # Create a response containing an string error message
            response = {
                'message': str(e)
            }

            return response, 500


def email_is_valid(email):
    """Check that the user's email is valid."""
    return re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
                    email)


def password_is_valid(password):
    """Check that the user's password is valid."""
    return re.match(r"(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{6,}", password)
