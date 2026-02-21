from http import HTTPStatus
import re

from flask import request, g
from flask_restx import Resource, Namespace, fields

from FlaskApp.domainmodel.category import CategoryType
from FlaskApp.infra.db import SessionLocal
from FlaskApp.infra.models import NullableString
from FlaskApp.infra.services import CREATED_RESPONSE, OK_RESPONSE, make_ok_response, models, validate_uuid
from FlaskApp.infra.services import require_auth
from FlaskApp.infra.unit_of_work import SqlAlchemyUnitOfWork
from FlaskApp.routes.categories.presentation import category_domain_to_json
from FlaskApp.routes.categories.services import get_categories, create_category, update_category, delete_category

ns = Namespace('categories', description='Operations related to categories')

# region Models
category_item_model = ns.model('CategoryItem', {
    'id': fields.String(readOnly=True, description='The unique identifier of a category',
                        example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4"),
    'name': fields.String(required=True, description='Category name', example="Groceries"),
    'description': fields.String(required=True, description='Category description', example="Monthly grocery expenses"),
    'colour': fields.String(required=True, description='Category colour in hex code', example="#FF5733"),
    'icon': NullableString(required=True, description='Category icon name', example="🥗"),
    'type': fields.String(required=True, description='Category type ("expense","income","all")', example="all"),
    'parent_category_id': NullableString(required=True, description='ID of the parent category, if any', example="")
})

editable_category_item_model = ns.model('EditableCategoryItem', {
    'name': fields.String(required=True, description='Category name', example="Groceries"),
    'description': fields.String(required=True, description='Category description', example="Monthly grocery expenses"),
    'colour': fields.String(required=True, description='Category colour in hex code', example="#FF5733"),
    'icon': NullableString(required=True, description='Category icon name', example="🥗"),
    'type': fields.String(required=True, description='Category type ("expense","income","all")', example="all"),
    'parent_category_id': NullableString(required=True, description='ID of the parent category, if any', example=None)
})

def validate_editable_category(data):
    if data['parent_category_id'] is not None:
        validate_uuid(data['parent_category_id'])
    if not data['type'] in CategoryType._value2member_map_:
        raise ValueError(f"Invalid category type: {data['type']}. Must be one of: {[e.value for e in CategoryType]}")
    if re.match(r'^#[0-9A-Fa-f]{6}$', data['colour']) is None:
        raise ValueError(f"Invalid colour: {data['colour']}. Must be a hex code in the format #RRGGBB.")
    if len(data['name']) > 100:
        raise ValueError("Name must be 100 characters or less.")
    if len(data['description']) > 255:
        raise ValueError("Description must be 255 characters or less.")

category_model = ns.model('Category', {
    "success": fields.Boolean(description='Indicates if the request was successful', example=True),
    "categories": fields.List(fields.Nested(category_item_model))
})

# endregion


@ns.route('')
class Category(Resource):

    @ns.response(HTTPStatus.OK, 'OK', category_model)
    @require_auth(ns=ns)
    def get(self):
        """Get all categories for the current user."""
        uow = SqlAlchemyUnitOfWork(SessionLocal)
        categories = get_categories(uow=uow, user=g.current_user)
        categories_json = [category_domain_to_json(category) for category in categories]
        return make_ok_response(categories=categories_json)

    @ns.response(HTTPStatus.CREATED, 'OK', models['OK'])
    @ns.response(HTTPStatus.BAD_REQUEST, 'Validation Error', models['BadRequest'])
    @ns.expect(editable_category_item_model, validate=True)
    @require_auth(ns=ns)
    def post(self):
        """Create a new category."""
        data = request.get_json()
        validate_editable_category(data)
        # Validate
        if data['parent_category_id'] is not None:
            validate_uuid(data['parent_category_id'])


        uow = SqlAlchemyUnitOfWork(SessionLocal)
        create_category(uow=uow, user=g.current_user, **data)
        return CREATED_RESPONSE




@ns.route('/<string:category_id>')
class CategoryById(Resource):
    @ns.response(HTTPStatus.OK, 'OK', models['OK'])
    @ns.response(HTTPStatus.BAD_REQUEST, 'Validation Error', models['BadRequest'])
    @ns.param('category_id', 'The unique identifier of the category to update', required=True, example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4")
    @ns.expect(editable_category_item_model, validate=True)
    @ns.doc(
        description="Update an existing category. All fields are required, even if not being updated. To change the "
                    "parent category, set parent_category_id to the new parent category ID or null to remove the "
                    "parent category.")
    @require_auth(ns=ns)
    def put(self, category_id):
        """Update an existing category."""
        data = request.get_json()

        # Validate
        validate_uuid(category_id)
        validate_editable_category(data)

        uow = SqlAlchemyUnitOfWork(SessionLocal)
        update_category(uow=uow, user=g.current_user, category_id=category_id, **data)
        return OK_RESPONSE

    @ns.response(HTTPStatus.OK, 'OK', models['OK'])
    @ns.response(HTTPStatus.BAD_REQUEST, 'Validation Error', models['BadRequest'])
    @ns.param('category_id', 'The unique identifier of the category to delete', required=True, example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4")
    @ns.doc(
        description="Delete an existing category. If the category has any transactions associated with it, the "
                    "category of those transactions will be set to null.")
    @require_auth(ns=ns)
    def delete(self, category_id):
        """Delete an existing category."""

        # Validate
        validate_uuid(category_id)

        uow = SqlAlchemyUnitOfWork(SessionLocal)

        delete_category(uow=uow, user=g.current_user, category_id=category_id)
        return OK_RESPONSE