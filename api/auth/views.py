from flask import request
from models.models import User
from flask_restplus import Resource
from api.bucketlists.serializers import email_and_password, api

ns = api.namespace('auth', description='User authentication')


@ns.route('/register')
class Registration(Resource):
    """This is where we register a new user."""

    @api.expect(email_and_password)
    def post(self):
        """Handle POST request at /auth/register."""

        post_data = request.json
        email = post_data.get('email')
        password = post_data.get('password')
        # Query to see if the user already exists
        user = User.query.filter_by(email=email).first()

        if not user:
            # There is no user so we'll try to register them
            try:
                user = User(email=email, password=password)
                user.save()

                response = {
                    'message': 'You registered successfully. Please log in.'
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
class Login(Resource):
    """This handles user login and access token generation."""

    @api.expect(email_and_password)
    def post(self):
        """Handle POST request for /auth/login"""

        post_data = request.json
        email = post_data.get('email')
        password = post_data.get('password')

        try:
            # Get the user object using their email (unique to every user)
            user = User.query.filter_by(email=email).first()

            # Try to authenticate the found user using their password
            if user and user.password_is_valid(password):
                # Generate the access token. This will be used as the authorization header
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
                    'message': 'Invalid email or password, Please try again'
                }
                return response, 401

        except Exception as e:
            # Create a response containing an string error message
            response = {
                'message': str(e)
            }
            # Return a server error using the HTTP Error Code 500 (Internal Server Error)
            return response, 500
