from flask_restplus import fields
from api.restplus import api

bucketitems = api.model('Items', {
    'id': fields.Integer,
    'name': fields.String(required=True, description='The name of a bucketlist item'),
    'bucketlist_id': fields.Integer,
    'date_created': fields.DateTime,
    'date_modified': fields.DateTime,
    'done': fields.Boolean
})

create_bucketoritem = api.model('Create', {
    'name': fields.String(required=True, description='The name of a bucketlist')
})

edit_item = api.model('Edit', {
    'name': fields.String(required=True, description='The name of a bucketlist'),
    'done': fields.Boolean(default=False)
})

buckets = api.model('Bucketlists', {
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
