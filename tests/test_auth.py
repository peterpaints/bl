import unittest
import json
from api import create_app, db


class AuthTestCase(unittest.TestCase):
    """Test case for the authentication blueprint."""

    def setUp(self):
        """Set up test variables."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client()
        self.user_data = {
            "email": "johndoe@test.com",
            "password": "Testpassw0rd"
        }

        with self.app.app_context():
            db.session.close()
            db.drop_all()
            db.create_all()

    def test_registration(self):
        """Test user registration works as designed."""
        res = self.client.post('api/v1/auth/register',
                               data=json.dumps(self.user_data),
                               headers={'content-type': 'application/json'})

        result = json.loads(res.data.decode())
        self.assertEqual(result['message'], "You registered successfully. Please log in.")
        self.assertEqual(res.status_code, 201)

    def test_already_registered_user(self):
        """Test that a user cannot be registered twice."""
        res = self.client.post('api/v1/auth/register',
                               data=json.dumps(self.user_data),
                               headers={'content-type': 'application/json'})
        self.assertEqual(res.status_code, 201)

        second_res = self.client.post('api/v1/auth/register',
                                      data=json.dumps(self.user_data),
                                      headers={'content-type': 'application/json'})
        self.assertEqual(second_res.status_code, 409)

        result = json.loads(second_res.data.decode())
        self.assertEqual(result['message'], "User already exists. Please login.")

    def test_user_login(self):
        """Test registered user can login."""
        res = self.client.post('api/v1/auth/register',
                               data=json.dumps(self.user_data),
                               headers={'content-type': 'application/json'})
        self.assertEqual(res.status_code, 201)

        login_res = self.client.post('api/v1/auth/login',
                                     data=json.dumps(self.user_data),
                                     headers={'content-type': 'application/json'})

        result = json.loads(login_res.data.decode())
        self.assertEqual(result['message'], "You logged in successfully.")
        self.assertEqual(login_res.status_code, 200)
        self.assertTrue(result['access_token'])

    def test_non_registered_user_login(self):
        """Test non registered users cannot login."""
        not_a_user = {
            'email': 'not_a_user@example.com',
            'password': 'nope'
        }

        res = self.client.post('api/v1/auth/login',
                               data=json.dumps(not_a_user),
                               headers={'content-type': 'application/json'})

        result = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 401)
        self.assertEqual(result['message'], "Invalid email or password, Please try again")

    def tearDown(self):
        """Teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()


if __name__ == "__main__":
    unittest.main()
