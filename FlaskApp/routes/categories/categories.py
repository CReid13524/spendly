from http import HTTPStatus

from flask import request, g
from flask_restx import Resource, Namespace, fields

from FlaskApp.infra.db import SessionLocal
from FlaskApp.infra.models import NullableString
from FlaskApp.infra.services import CREATED_RESPONSE, OK_RESPONSE, make_ok_response, models
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

new_category_item_model = ns.model('NewCategoryItem', {
    'name': fields.String(required=True, description='Category name', example="Groceries"),
    'description': fields.String(required=True, description='Category description', example="Monthly grocery expenses"),
    'colour': fields.String(required=True, description='Category colour in hex code', example="#FF5733"),
    'icon': NullableString(required=True, description='Category icon name', example="🥗"),
    'type': fields.String(required=True, description='Category type ("expense","income","all")', example="all"),
    'parent_category_id': NullableString(required=True, description='ID of the parent category, if any', example=None)
})

category_model = ns.model('Category', {
    "success": fields.Boolean(description='Indicates if the request was successful', example=True),
    "categories": fields.List(fields.Nested(category_item_model))
})

category_id_model = ns.model('category_id', {
    'id': fields.String(required=True, description='The unique identifier of a category',
                        example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4")
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
    @ns.expect(new_category_item_model, validate=True)
    @require_auth(ns=ns)
    def post(self):
        """Create a new category."""
        uow = SqlAlchemyUnitOfWork(SessionLocal)
        data = request.get_json()
        create_category(uow=uow, user=g.current_user, **data)
        return CREATED_RESPONSE

    @ns.response(HTTPStatus.OK, 'OK', models['OK'])
    @ns.expect(category_item_model, validate=True)
    @ns.doc(
        description="Update an existing category. All fields are required, even if not being updated. To change the "
                    "parent category, set parent_category_id to the new parent category ID or null to remove the "
                    "parent category.")
    @require_auth(ns=ns)
    def put(self):
        """Update an existing category."""
        uow = SqlAlchemyUnitOfWork(SessionLocal)
        data = request.get_json()
        update_category(uow=uow, user=g.current_user, **data)
        return OK_RESPONSE

    @ns.response(HTTPStatus.OK, 'OK', models['OK'])
    @ns.expect(category_id_model, validate=True)
    @ns.doc(
        description="Delete an existing category. If the category has any transactions associated with it, the "
                    "category of those transactions will be set to null.")
    @require_auth(ns=ns)
    def delete(self):
        """Delete an existing category."""
        uow = SqlAlchemyUnitOfWork(SessionLocal)
        data = request.get_json()
        delete_category(uow=uow, user=g.current_user, category_id=data['id'])
        return OK_RESPONSE
