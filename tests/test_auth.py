import json

from base import BaseTestCase


class AuthTestCase(BaseTestCase):
    """Test case for the authentication blueprint."""

    def test_registration(self):
        """Test user registration works as designed."""
        response = self.register_user()

        result = json.loads(response.data.decode())

        self.assertEqual(result['message'],
                         'You registered successfully. Please log in.')
        self.assertEqual(response.status_code, 201)

    def test_registration_with_invalid_email(self):
        """Test that a user cannot register with an invalid email address."""
        data = {
            "email": "123456",
            "password": "Testpassw0rd"
        }

        res = self.client.post('api/v1/auth/register',
                               data=json.dumps(data),
                               headers={'content-type': 'application/json'})

        result = json.loads(res.data.decode())

        self.assertEqual(result['message'],
                         'Your email is invalid. Please enter a valid email.')
        self.assertEqual(res.status_code, 400)

    def test_registration_with_invalid_password(self):
        """Test that a user cannot register with an invalid password."""
        data = {
            "email": "test@example.com",
            "password": "testpassw0rd"
        }

        res = self.client.post('api/v1/auth/register',
                               data=json.dumps(data),
                               headers={'content-type': 'application/json'})

        result = json.loads(res.data.decode())

        self.assertEqual(result['message'],
                         'Your password should contain at least one number, \
one lowercase, one uppercase letter and at least six characters')
        self.assertEqual(res.status_code, 400)

    def test_already_registered_user(self):
        """Test that a user cannot be registered twice."""
        response = self.register_user()

        self.assertEqual(response.status_code, 201)

        second_response = self.register_user()

        self.assertEqual(second_response.status_code, 409)

        result = json.loads(second_response.data.decode())

        self.assertEqual(result['message'],
                         "User already exists. Please login.")

    def test_user_login(self):
        """Test registered user can login."""
        self.register_user()
        login_response = self.login_user()

        result = json.loads(login_response.data.decode())

        self.assertEqual(result['message'], "You logged in successfully.")
        self.assertEqual(login_response.status_code, 200)
        self.assertTrue(result['access_token'])

    def test_non_registered_user_login(self):
        """Test non registered users cannot login."""
        not_a_user = {
            'email': 'not_a_user@example.com',
            'password': 'nope'
        }

        response = self.client.post('api/v1/auth/login',
                                    data=json.dumps(not_a_user),
                                    headers={'content-type': 'application/json'})

        result = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 401)
        self.assertEqual(result['message'],
                         "Invalid email or password. Please try again")
