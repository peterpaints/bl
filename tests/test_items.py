import unittest
import json

from api import create_app, db


class ItemsTestCase(unittest.TestCase):
    """This class represents the bucketlist items test case."""

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
            headers={'Authorization': access_token, 'content-type': 'application/json'},
            data=json.dumps(self.bucketlist))

        self.assertEqual(res.status_code, 201)
        return access_token

    def test_item_creation(self):
        """Test the API can create a bucketlist item."""
        access_token = self.create_bucketlist()

        res = self.client.get(
            'api/v1/bucketlists/',
            headers=dict(Authorization=access_token),
        )

        self.assertEqual(res.status_code, 200)
        self.assertIn('TomorrowLand', str(res.data))

        bucket_id = json.loads(res.data.decode())[0]['id']

        item = self.client.post(
            'api/v1/bucketlists/{}/items'.format(bucket_id),
            headers={'Authorization': access_token, 'content-type': 'application/json'},
            data=json.dumps(self.item))

        self.assertEqual(item.status_code, 201)

        confirm = self.client.get(
            'api/v1/bucketlists/{}'.format(bucket_id),
            headers=dict(Authorization=access_token),
        )

        self.assertEqual(confirm.status_code, 200)
        self.assertIn('tickets cash', str(json.loads(confirm.data.decode())['items'][0]))

    def test_bucketlist_items_can_be_edited(self):
        """Test API can edit an existing bucketlist item."""
        access_token = self.create_bucketlist()

        res = self.client.get(
            'api/v1/bucketlists/',
            headers=dict(Authorization=access_token),
        )

        self.assertEqual(res.status_code, 200)
        self.assertIn('TomorrowLand', str(res.data))

        bucket_id = json.loads(res.data.decode())[0]['id']

        item = self.client.post(
            'api/v1/bucketlists/{}/items'.format(bucket_id),
            headers={'Authorization': access_token, 'content-type': 'application/json'},
            data=json.dumps(self.item))

        self.assertEqual(item.status_code, 201)

        item_id = json.loads(item.data.decode())['id']

        update = self.client.put(
            'api/v1/bucketlists/{}/items/{}'.format(bucket_id, item_id),
            headers={'Authorization': access_token, 'content-type': 'application/json'},
            data=json.dumps({
                "name": "Rob a bank first"
            }))

        self.assertEqual(update.status_code, 200)

        confirm = self.client.get(
            'api/v1/bucketlists/{}'.format(bucket_id),
            headers=dict(Authorization=access_token))

        self.assertIn('bank first', json.loads(confirm.data.decode())['items'][0]['name'])

    def test_bucketlist_item_deletion(self):
        """Test API can delete an existing bucketlist item."""
        access_token = self.create_bucketlist()

        res = self.client.get(
            'api/v1/bucketlists/',
            headers=dict(Authorization=access_token),
        )

        self.assertEqual(res.status_code, 200)
        self.assertIn('TomorrowLand', str(res.data))

        bucket_id = json.loads(res.data.decode())[0]['id']

        item = self.client.post(
            'api/v1/bucketlists/{}/items'.format(bucket_id),
            headers={'Authorization': access_token, 'content-type': 'application/json'},
            data=json.dumps(self.item))

        self.assertEqual(item.status_code, 201)

        item_id = json.loads(item.data.decode())['id']

        remove = self.client.delete(
            'api/v1/bucketlists/{}/items/{}'.format(bucket_id, item_id),
            headers=dict(Authorization=access_token))

        self.assertEqual(remove.status_code, 200)

        confirm = self.client.get(
            'api/v1/bucketlists/{}'.format(bucket_id, item_id),
            headers=dict(Authorization=access_token))

        self.assertListEqual(json.loads(confirm.data.decode())['items'], [])

    def tearDown(self):
        """Teardown all initialized variables."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()


if __name__ == "__main__":
    unittest.main()
