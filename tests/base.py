import json
import unittest

from api import create_app, db


class BaseTestCase(unittest.TestCase):
    """Define a base testcase, with a reusable setup."""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client()

        self.bucketlist = {
            'name': 'Attend TomorrowLand'
        }

        self.item = {
            'name': 'Save up tickets cash'
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

    def create_bucketlist(self):
        """Sample bucketlist to be used in our tests."""
        self.register_user()
        result = self.login_user()

        access_token = json.loads(result.data.decode())['access_token']

        res = self.client.post(
            'api/v1/bucketlists/',
            headers={'Authorization': access_token,
                     'content-type': 'application/json'},
            data=json.dumps(self.bucketlist))

        self.assertEqual(res.status_code, 201)
        bucket_id = json.loads(res.data.decode())['id']
        return [access_token, bucket_id]

    def create_bucketlist_item(self):
        """Sample bucketlist to be used in our tests."""
        bucket = self.create_bucketlist()
        access_token = bucket[0]
        bucket_id = bucket[1]

        res = self.client.get(
            'api/v1/bucketlists/',
            headers=dict(Authorization=access_token),
        )

        self.assertEqual(res.status_code, 200)
        self.assertIn('TomorrowLand', str(res.data))

        item = self.client.post(
            'api/v1/bucketlists/{}/items'.format(bucket_id),
            headers={'Authorization': access_token,
                     'content-type': 'application/json'},
            data=json.dumps(self.item))

        self.assertEqual(item.status_code, 201)
        item_id = json.loads(item.data.decode())['id']

        return [access_token, bucket_id, item_id]

    def tearDown(self):
        """Teardown all initialized variables."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()


if __name__ == "__main__":
    unittest.main()
