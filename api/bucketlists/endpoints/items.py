from flask import request

from api import bucketlists_namespace
from api.bucketlists.serializers import (bucketitems, create_bucketoritem,
                                         edit_item)
from api.decorators import check_access_token
from api.restplus import api
from flask_restplus import Resource, abort
from models.models import Bucketlist, Item

ns = bucketlists_namespace


@ns.route('/<int:id>/items')
@api.response(201, 'Successfully created.')
@api.header('Authorization', 'JSON Web Token', required=True)
class ItemsEndPoint(Resource):

    @check_access_token
    @api.expect(create_bucketoritem)
    @api.marshal_with(bucketitems)
    def post(self, id):
        """Create a bucketlist item under the bucketlist with the given id."""
        name = request.json.get('name')
        if name:
            item = Item(name=name, bucketlist_id=id)
            item.save()

            return item, 201


@ns.route('/<int:id>/items/<int:item_id>')
@api.response(404, 'There is no bucketlist with id ~')
@api.header('Authorization', 'JSON Web Token', required=True)
class ItemsManipulation(Resource):

    @check_access_token
    @api.expect(edit_item)
    @api.marshal_with(bucketitems)
    def put(self, id, item_id):
        """Edit a bucketlist item's name or done status."""
        # Get the bucketlist with the id specified from the URL (<int:id>)
        bucketlist = Bucketlist.query.filter_by(id=id,
                                                created_by=request.user_id)
        bucketlist = bucketlist.first()
        if not bucketlist:
            abort(404, 'This user has no bucketlist with id ' + str(id))
        else:
            item = Item.query.filter_by(id=item_id,
                                        bucketlist_id=bucketlist.id).first()
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
                abort(404, 'There is no bucket item with id ' + str(item_id))

    @check_access_token
    def delete(self, id, item_id):
        """Delete a bucketlist item under the bucketlist with the given id."""
        bucketlist = Bucketlist.query.filter_by(id=id,
                                                created_by=request.user_id)
        bucketlist = bucketlist.first()
        if not bucketlist:
            abort(404, 'This user has no bucketlist with id ' + str(id))
        else:
            item = Item.query.filter_by(id=item_id,
                                        bucketlist_id=bucketlist.id).first()
            if item:
                item.delete()
                return 'Item id ' + str(id) + ' successfully deleted', 200
            else:
                abort(404, 'There is no item with id ' + str(item_id))
