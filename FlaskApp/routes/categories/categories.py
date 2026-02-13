from flask import request, g
from flask_restx import Resource, Namespace, fields
from FlaskApp.domainmodel import user
from FlaskApp.infra.models import register_global_models_to_namespace
from FlaskApp.infra.db import SessionLocal
from FlaskApp.infra.services import require_auth
from FlaskApp.infra.unit_of_work import SqlAlchemyUnitOfWork
from FlaskApp.routes.categories.presentation import category_domain_to_json
from FlaskApp.routes.categories.services import  get_categories, create_category, update_category, delete_category
from http import HTTPStatus

ns = Namespace('categories', description='Operations related to categories')

category_item_model = ns.model('CategoryItem', {
    'id': fields.String(readOnly=True, description='The unique identifier of a category', example="123456789abcdefabcdefabcdefabcde"),
    'name': fields.String(required=True, description='Category name', example="Groceries"),
    'description': fields.String(required=True, description='Category description', example="Monthly grocery expenses"),
    'colour': fields.String(required=True, description='Category colour in hex code', example="#FF5733"),
    'icon': fields.String(required=True, description='Category icon name', example="🥗"),
    'type': fields.String(required=True, description='Category type ("expense","income","all")', example="all"),
    'parent_category_id': fields.String(description='ID of the parent category, if any', example="")
})

new_category_item_model = ns.model('NewCategoryItem', {
    'name': fields.String(required=True, description='Category name', example="Groceries"),
    'description': fields.String(required=True, description='Category description', example="Monthly grocery expenses"),
    'colour': fields.String(required=True, description='Category colour in hex code', example="#FF5733"),
    'icon': fields.String(required=True, description='Category icon name', example="🥗"),
    'type': fields.String(required=True, description='Category type ("expense","income","all")', example="all"),
    'parent_category_id': fields.String(description='ID of the parent category, if any', example="")
})

category_model = ns.model('Category', {
    "success": fields.Boolean(description='Indicates if the request was successful', example=True),
    "categories": fields.List(fields.Nested(category_item_model))
})

category_id_model = ns.model('category_id', {
    'id': fields.String(required=True, description='The unique identifier of a category', example="123456789abcdefabcdefabcdefabcde")
})
@ns.route('')
class Category(Resource):

    @ns.response(HTTPStatus.OK, 'Success', category_model)
    @require_auth(ns=ns)
    def get(self):
        """Get all categories for the current user."""
        uow = SqlAlchemyUnitOfWork(SessionLocal)
        categories = get_categories(uow=uow, user=g.current_user)
        categories_json = [category_domain_to_json(category) for category in categories]
        return {"success": True, "categories": categories_json}, HTTPStatus.OK

    @ns.response(HTTPStatus.CREATED, 'Success')
    @ns.expect(new_category_item_model, validate=True)
    @require_auth(ns=ns)
    def post(self):
        """Create a new category."""
        uow = SqlAlchemyUnitOfWork(SessionLocal)
        data = request.get_json()
        create_category(uow=uow, user=g.current_user, **data)
        return {"success": True}, HTTPStatus.CREATED

    @ns.response(HTTPStatus.OK, 'Success')
    @ns.expect(category_item_model, validate=True)
    @require_auth(ns=ns)
    def put(self):
        """Update an existing category."""
        uow = SqlAlchemyUnitOfWork(SessionLocal)
        data = request.get_json()
        update_category(uow=uow, user=g.current_user, **data)
        return {"success": True}, HTTPStatus.OK

    @ns.response(HTTPStatus.OK, 'Success')
    @ns.expect(category_id_model, validate=True)
    @require_auth(ns=ns)
    def delete(self):
        """Delete an existing category."""
        uow = SqlAlchemyUnitOfWork(SessionLocal)
        data = request.get_json()
        delete_category(uow=uow, category_id=data['id'])
        return {"success": True}, HTTPStatus.OK