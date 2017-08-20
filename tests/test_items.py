import json

from base import BaseTestCase


class ItemsTestCase(BaseTestCase):
    """This class represents the bucketlist items test case."""

    def test_item_creation(self):
        """Test the API can create a bucketlist item."""
        item = self.create_bucketlist_item()
        access_token = item[0]
        bucket_id = item[1]

        confirm = self.client.get(
            'api/v1/bucketlists/{}'.format(bucket_id),
            headers=dict(Authorization=access_token),
        )

        self.assertEqual(confirm.status_code, 200)
        self.assertIn('tickets cash',
                      str(json.loads(confirm.data.decode())['items'][0]))

    def test_bucketlist_items_can_be_edited(self):
        """Test API can edit an existing bucketlist item."""
        item = self.create_bucketlist_item()
        access_token = item[0]
        bucket_id = item[1]
        item_id = item[2]

        update = self.client.put(
            'api/v1/bucketlists/{}/items/{}'.format(bucket_id, item_id),
            headers={'Authorization': access_token,
                     'content-type': 'application/json'},
            data=json.dumps({
                "name": "Rob a bank first"
            }))

        self.assertEqual(update.status_code, 200)

        confirm = self.client.get(
            'api/v1/bucketlists/{}'.format(bucket_id),
            headers=dict(Authorization=access_token))

        self.assertIn('bank first',
                      json.loads(confirm.data.decode())['items'][0]['name'])

    def test_bucketlist_item_deletion(self):
        """Test API can delete an existing bucketlist item."""
        item = self.create_bucketlist_item()
        access_token = item[0]
        bucket_id = item[1]
        item_id = item[2]

        remove = self.client.delete(
            'api/v1/bucketlists/{}/items/{}'.format(bucket_id, item_id),
            headers=dict(Authorization=access_token))

        self.assertEqual(remove.status_code, 200)

        confirm = self.client.get(
            'api/v1/bucketlists/{}'.format(bucket_id, item_id),
            headers=dict(Authorization=access_token))

        self.assertListEqual(json.loads(confirm.data.decode())['items'], [])
