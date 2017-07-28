import unittest
import json

from api import create_app, db


class BucketlistTestCase(unittest.TestCase):
    """This class represents the bucketlist test case."""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client()
        self.bucketlist = {
            'name': 'Attend TomorrowLand'
        }

        self.user_data = {
            "email": "johndoe@test.com",
            "password": "Testpassw0rd"
        }

        with self.app.app_context():
            db.session.close()
            db.drop_all()
            db.create_all()

    def register_user(self):
        """Register a test user."""
        return self.client.post('api/v1/auth/register',
                                data=json.dumps(self.user_data),
                                headers={'content-type': 'application/json'})

    def login_user(self):
        """Log in a test user."""
        return self.client.post('api/v1/auth/login',
                                data=json.dumps(self.user_data),
                                headers={'content-type': 'application/json'})

    def test_bucketlist_creation(self):
        """Test the API can create a bucketlist."""
        self.register_user()
        result = self.login_user()

        access_token = json.loads(result.data.decode())['access_token']

        res = self.client.post(
            'api/v1/bucketlists/',
            headers={'Authorization': access_token, 'content-type': 'application/json'},
            data=json.dumps(self.bucketlist))

        self.assertEqual(res.status_code, 201)
        self.assertIn('TomorrowLand', str(res.data))

    def test_api_can_get_all_bucketlists(self):
        """Test API can get a bucketlist."""
        self.register_user()
        result = self.login_user()

        access_token = json.loads(result.data.decode())['access_token']

        res = self.client.post(
            'api/v1/bucketlists/',
            headers={'Authorization': access_token, 'content-type': 'application/json'},
            data=json.dumps(self.bucketlist))

        self.assertEqual(res.status_code, 201)

        res = self.client.get(
            'api/v1/bucketlists/',
            headers=dict(Authorization=access_token),
        )

        self.assertEqual(res.status_code, 200)
        self.assertIn('TomorrowLand', str(res.data))

    def test_api_can_get_bucketlist_by_id(self):
        """Test API can get a single bucketlist by using it's id."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client.post(
            'api/v1/bucketlists/',
            headers={'Authorization': access_token, 'content-type': 'application/json'},
            data=json.dumps(self.bucketlist))

        self.assertEqual(res.status_code, 201)

        results = json.loads(res.data.decode())

        rv = self.client.get(
            'api/v1/bucketlists/{}'.format(results['id']),
            headers=dict(Authorization=access_token))

        self.assertEqual(rv.status_code, 200)
        self.assertIn('TomorrowLand', str(rv.data))

    def test_get_all_bucketlists_with_pagination_args(self):
        """Test API pagination."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client.post(
            'api/v1/bucketlists/',
            headers={'Authorization': access_token, 'content-type': 'application/json'},
            data=json.dumps(self.bucketlist))

        self.assertEqual(res.status_code, 201)

        rv = self.client.get(
            '/api/v1/bucketlists/?page=1&per_page=5',
            headers=dict(Authorization=access_token))

        self.assertEqual(rv.status_code, 200)
        self.assertIn('TomorrowLand', str(rv.data))

        rv2 = self.client.get(
            '/api/v1/bucketlists/?page=2&per_page=5',
            headers=dict(Authorization=access_token))

        self.assertEqual(rv2.status_code, 200)
        self.assertNotIn('TomorrowLand', str(rv2.data))

    def test_bucketlist_can_be_edited(self):
        """Test API can edit an existing bucketlist."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client.post(
            'api/v1/bucketlists/',
            headers={'Authorization': access_token, 'content-type': 'application/json'},
            data=json.dumps({'name': 'Meet Elon'}))
        self.assertEqual(res.status_code, 201)

        result = json.loads(res.data.decode())

        update = self.client.put(
            'api/v1/bucketlists/{}'.format(result['id']),
            headers={'Authorization': access_token, 'content-type': 'application/json'},
            data=json.dumps({
                "name": "Start a company with Elon"
            }))

        self.assertEqual(update.status_code, 200)

        confirm = self.client.get(
            'api/v1/bucketlists/{}'.format(result['id']),
            headers=dict(Authorization=access_token))

        self.assertIn('with Elon', str(confirm.data))

    def test_bucketlist_deletion(self):
        """Test API can delete an existing bucketlist."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client.post(
            'api/v1/bucketlists/',
            headers={'Authorization': access_token, 'content-type': 'application/json'},
            data=json.dumps({'name': 'Meet Elon'}))
        self.assertEqual(res.status_code, 201)

        result = json.loads(res.data.decode())

        remove = self.client.delete(
            'api/v1/bucketlists/{}'.format(result['id']),
            headers=dict(Authorization=access_token),)

        self.assertEqual(remove.status_code, 200)

        confirm = self.client.get(
            'api/v1/bucketlists/{}'.format(result['id']),
            headers=dict(Authorization=access_token))

        self.assertEqual(confirm.status_code, 404)

    def tearDown(self):
        """Teardown all initialized variables."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()


if __name__ == "__main__":
    unittest.main()
