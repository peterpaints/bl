from flask import request
from flask_restplus import Resource, abort
from api.bucketlists.serializers import create_bucketoritem, buckets
from api.bucketlists.parsers import pagination_arguments
from api.restplus import api
from models.models import Bucketlist, User


ns = api.namespace('bucketlists', description='Bucketlist manipulation')


@ns.route('/')
@api.header('Authorization', 'JSON Web Token', required=True)
class BucketListEndPoint(Resource):

    @api.expect(pagination_arguments, validate=True)
    @api.marshal_list_with(buckets)
    def get(self):
        """Return list of bucketlists."""
        # Get the access token from the header
        access_token = request.headers.get('Authorization')

        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)

            if not isinstance(user_id, str):
                args = pagination_arguments.parse_args(request)
                page = args.get('page', 1)
                per_page = args.get('per_page', 5)
                # Go ahead and handle the request, the user is authenticated
                # GET all the bucketlists created by this user
                try:
                    bucketlists_query = Bucketlist.query.filter_by(created_by=user_id)
                    if not bucketlists_query:
                        abort(404, 'There are no bucketlists')
                    else:
                        bucketlists = bucketlists_query.paginate(page, per_page, error_out=False)
                        return bucketlists.items, 200
                except Exception as e:
                    abort(404, str(e))
            else:
                # user is not legit, so the payload is an error message
                abort(401, user_id)

    @api.expect(create_bucketoritem)
    @api.marshal_with(buckets)
    def post(self):
        # Get the access token from the header
        access_token = request.headers.get('Authorization')

        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)

            if not isinstance(user_id, str):
                # Go ahead and handle the request, the user is authenticated

                name = request.json.get('name')
                if name:
                    bucketlist = Bucketlist(name=name, created_by=user_id)
                    bucketlist.save()

                    return bucketlist, 201


@ns.route('/<int:id>')
@api.header('Authorization', 'JSON Web Token', required=True)
class BucketlistManipulation(Resource):

    @api.marshal_with(buckets)
    def get(self, id):
        # get the access token from the authorization header

        access_token = request.headers.get('Authorization')

        if access_token:
            # Get the user id related to this access token
            user_id = User.decode_token(access_token)

            if not isinstance(user_id, str):
                # If the id is not a string(error), we have a user id
                # Get the bucketlist with the id specified from the URL (<int:id>)
                bucketlist = Bucketlist.query.filter_by(id=id).first()
                if bucketlist:
                    return bucketlist, 200
                    # There is no bucketlist with this ID for this User, so
                    # Raise an HTTPException with a 404 not found status code
                else:
                    abort(404, 'There is no bucketlist with id ' + str(id))
            else:
                abort(401, user_id)

    @api.expect(create_bucketoritem)
    @api.marshal_with(buckets)
    def put(self, id):

        access_token = request.headers.get('Authorization')

        if access_token:
            # Get the user id related to this access token
            user_id = User.decode_token(access_token)

            if not isinstance(user_id, str):

                name = request.json.get('name')
                bucketlist = Bucketlist.query.filter_by(id=id).first()
                if name:
                    if bucketlist:
                        bucketlist.name = name
                        bucketlist.save()

                        return bucketlist, 200
                        # There is no bucketlist with this ID for this User, so
                        # Raise an HTTPException with a 404 not found status code
                    else:
                        abort(404, 'There is no bucketlist with id ' + str(id))
            else:
                abort(401, user_id)

    def delete(self, id):

        access_token = request.headers.get('Authorization')

        if access_token:
            # Get the user id related to this access token
            user_id = User.decode_token(access_token)

            if not isinstance(user_id, str):
                bucketlist = Bucketlist.query.filter_by(id=id).first()

                if bucketlist:
                    bucketlist.delete()

                    return 'Bucketlist id ' + str(id) + ' successfully deleted', 200

                else:
                    abort(404, 'There is no bucketlist with id ' + str(id))
        else:
            abort(401, user_id)
