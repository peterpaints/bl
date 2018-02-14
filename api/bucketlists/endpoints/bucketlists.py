from flask import request

from api.bucketlists.parsers import pagination_arguments
from api.bucketlists.serializers import buckets, create_bucketoritem
from api.decorators import check_access_token
from api.restplus import api
from flask_restplus import Resource, abort
from models.models import Bucketlist

ns = api.namespace('bucketlists', description='Bucketlist manipulation')


@ns.route('/')
@api.response(201, 'Successfully created.')
@api.response(404, 'There is no bucketlist with id ~')
@api.header('Authorization', 'JSON Web Token', required=True)
class BucketListEndPoint(Resource):

    @check_access_token
    @api.expect(pagination_arguments, validate=True)
    @api.marshal_list_with(buckets)
    def get(self):
        """Return list of bucketlists."""
        args = pagination_arguments.parse_args(request)
        page = args.get('page', 1)
        per_page = args.get('per_page', 5)
        find = args.get('q')

        # GET all the bucketlists created by this user
        try:
            bucketlists_query = Bucketlist.query.filter_by(
                                created_by=request.user_id)
            if find:
                bucketlists = bucketlists_query.filter(
                                Bucketlist.name.ilike('%' + find + '%'))
                return bucketlists.paginate(page, per_page,
                                            error_out=False).items, 200
            else:
                bucketlists = bucketlists_query.paginate(page, per_page,
                                                         error_out=False)
                return bucketlists.items, 200
        except Exception as e:
            abort(404, str(e))

    @check_access_token
    @api.expect(create_bucketoritem)
    @api.marshal_with(buckets)
    def post(self):
        """Create a bucketlist."""
        name = request.json.get('name')
        if name:
            bucketlist = Bucketlist(name=name, created_by=request.user_id)
            bucketlist.save()

            return bucketlist, 201


@ns.route('/<int:id>')
@api.header('Authorization', 'JSON Web Token', required=True)
class BucketlistManipulation(Resource):

    @check_access_token
    @api.marshal_with(buckets)
    def get(self, id):
        """Return the bucketlist with the provided id."""
        # Get the bucketlist with the id specified from the URL (<int:id>)
        bucketlist = Bucketlist.query.filter_by(id=id,
                                                created_by=request.user_id)
        bucketlist = bucketlist.first()
        if bucketlist:
            return bucketlist, 200
            # There is no bucketlist with this ID for this User, so
            # Raise an HTTPException with a 404 not found status code
        else:
            abort(404, 'There is no bucketlist with id ' + str(id))

    @check_access_token
    @api.expect(create_bucketoritem)
    @api.marshal_with(buckets)
    def put(self, id):
        """Edit the name of a bucketlist."""
        name = request.json.get('name')
        bucketlist = Bucketlist.query.filter_by(id=id,
                                                created_by=request.user_id)
        bucketlist = bucketlist.first()
        if not bucketlist:
            abort(404, 'This user has no bucketlist with id ' + str(id))
        if name:
            bucketlist.name = name
            bucketlist.save()

            return bucketlist, 200

    @check_access_token
    def delete(self, id):
        """Delete a particular bucketlist."""
        bucketlist = Bucketlist.query.filter_by(id=id,
                                                created_by=request.user_id)
        bucketlist = bucketlist.first()
        if not bucketlist:
            abort(404, 'This user has no bucketlist with id ' + str(id))
        else:
            bucketlist.delete()
            return 'Bucketlist id ' + str(id) + ' successfully deleted', 200
