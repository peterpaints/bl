from flask_restplus import fields
from api.restplus import api

bucketitems = api.model('Bucketlists', {
    'id': fields.Integer,
    'name': fields.String(required=True, description='The name of a bucketlist item'),
    'bucketlist_id': fields.Integer,
    'date_created': fields.DateTime,
    'date_modified': fields.DateTime,
    'done': fields.Boolean
})

create_bucket = api.model('Bucketlists', {
    'name': fields.String(required=True, description='The name of a bucketlist')
})

buckets = api.model('Items', {
    'id': fields.Integer,
    'name': fields.String(required=True, description='The name of a bucketlist'),
    'items': fields.List(fields.Nested(bucketitems)),
    'date_created': fields.DateTime,
    'date_modified': fields.DateTime,
    'created_by': fields.Integer
})

email_and_password = api.model('Email_and_password', {
    'email': fields.String(required=True),
    'password': fields.String(required=True)
})
