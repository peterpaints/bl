import json

from base import BaseTestCase


class BucketlistTestCase(BaseTestCase):
    """This class represents the bucketlist test case."""

    def test_api_can_get_all_bucketlists(self):
        """Test API can get a bucketlist."""
        bucket = self.create_bucketlist()
        access_token = bucket[0]

        response = self.client.get(
            'api/v1/bucketlists/',
            headers=dict(Authorization=access_token),
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('TomorrowLand', str(response.data))

    def test_api_can_get_bucketlist_by_id(self):
        """Test API can get a single bucketlist by using it's id."""
        bucket = self.create_bucketlist()
        access_token = bucket[0]
        bucket_id = bucket[1]

        response = self.client.get(
            'api/v1/bucketlists/{}'.format(bucket_id),
            headers=dict(Authorization=access_token))

        self.assertEqual(response.status_code, 200)
        self.assertIn('TomorrowLand', str(response.data))

    def test_get_all_bucketlists_with_pagination_args(self):
        """Test API pagination."""
        bucket = self.create_bucketlist()
        access_token = bucket[0]

        response = self.client.get(
            '/api/v1/bucketlists/?page=1&per_page=5',
            headers=dict(Authorization=access_token))

        self.assertEqual(response.status_code, 200)
        self.assertIn('TomorrowLand', str(response.data))

        response2 = self.client.get(
            '/api/v1/bucketlists/?page=2&per_page=5',
            headers=dict(Authorization=access_token))

        self.assertEqual(response2.status_code, 200)
        self.assertNotIn('TomorrowLand', str(response2.data))

    def test_bucketlist_can_be_edited(self):
        """Test API can edit an existing bucketlist."""
        bucket = self.create_bucketlist()
        access_token = bucket[0]
        bucket_id = bucket[1]

        update = self.client.put(
            'api/v1/bucketlists/{}'.format(bucket_id),
            headers={'Authorization': access_token,
                     'content-type': 'application/json'},
            data=json.dumps({
                "name": "Start a company with Elon"
            }))

        self.assertEqual(update.status_code, 200)

        confirm = self.client.get(
            'api/v1/bucketlists/{}'.format(bucket_id),
            headers=dict(Authorization=access_token))

        self.assertIn('with Elon', str(confirm.data))

    def test_bucketlist_deletion(self):
        """Test API can delete an existing bucketlist."""
        bucket = self.create_bucketlist()
        access_token = bucket[0]
        bucket_id = bucket[1]

        remove = self.client.delete(
            'api/v1/bucketlists/{}'.format(bucket_id),
            headers=dict(Authorization=access_token),)

        self.assertEqual(remove.status_code, 200)

        confirm = self.client.get(
            'api/v1/bucketlists/{}'.format(bucket_id),
            headers=dict(Authorization=access_token))

        self.assertEqual(confirm.status_code, 404)
