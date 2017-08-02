from flask import request
from api import bucketlists_namespace
from flask_restplus import Resource, abort
from api.bucketlists.serializers import bucketitems, create_bucketoritem, edit_item
from api.restplus import api
from models.models import User, Item, Bucketlist


ns = bucketlists_namespace


@ns.route('/<int:id>/items')
@api.header('Authorization', 'JSON Web Token', required=True)
class ItemsEndPoint(Resource):

    @api.expect(create_bucketoritem)
    @api.marshal_with(bucketitems)
    def post(self, id):
        """Create a bucketlist item under the bucketlist with the given id."""
        # Get the access token from the header
        access_token = request.headers.get('Authorization')

        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)

            if not isinstance(user_id, str):
                # Go ahead and handle the request, the user is authenticated

                name = request.json.get('name')
                if name:
                    item = Item(name=name, bucketlist_id=id)
                    item.save()

                    return item, 201


@ns.route('/<int:id>/items/<int:item_id>')
@api.header('Authorization', 'JSON Web Token', required=True)
class ItemsManipulation(Resource):

    @api.expect(edit_item)
    @api.marshal_with(bucketitems)
    def put(self, id, item_id):
        """Edit a bucketlist item's name or done status."""
        # get the access token from the authorization header
        access_token = request.headers.get('Authorization')

        if access_token:
            # Get the user id related to this access token
            user_id = User.decode_token(access_token)

            if not isinstance(user_id, str):
                # If the id is not a string(error), we have a user id
                # Get the bucketlist with the id specified from the URL (<int:id>)
                bucketlist = Bucketlist.query.filter_by(id=id, created_by=user_id).first()
                if not bucketlist:
                    abort(404, 'This user has no bucketlist with id ' + str(id))
                else:
                    item = Item.query.filter_by(id=item_id, bucketlist_id=bucketlist.id).first()
                    name = request.json.get('name')
                    done = request.json.get('done')
                    if item:
                        item.name = name
                        item.done = done
                        item.save()
                        return item, 200
                        # There is no bucketlist with this ID for this User, so
                        # Raise an HTTPException with a 404 not found status code
                    else:
                        abort(404, 'There is no bucketlist item with id ' + str(item_id))
            else:
                abort(401, user_id)

    def delete(self, id, item_id):
        """Delete a bucketlist item under the bucketlist with the given id."""
        access_token = request.headers.get('Authorization')

        if access_token:
            # Get the user id related to this access token
            user_id = User.decode_token(access_token)

            if not isinstance(user_id, str):
                bucketlist = Bucketlist.query.filter_by(id=id, created_by=user_id).first()
                if not bucketlist:
                    abort(404, 'This user has no bucketlist with id ' + str(id))
                else:
                    item = Item.query.filter_by(id=item_id, bucketlist_id=bucketlist.id).first()

                    if item:
                        item.delete()
                        return 'Item id ' + str(id) + ' successfully deleted', 200

                    else:
                        abort(404, 'There is no item with id ' + str(item_id))
        else:
            abort(401, user_id)
