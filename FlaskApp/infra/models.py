from http import HTTPStatus
from flask_restx import fields, Namespace, Api

models = {
    'RequireAuth': {
        'success': fields.Boolean(description='Indicates if the request was successful', example=False),
        'message': fields.String(description='Error message if authentication fails', example="Authentication required")
    },
    'InternalServerError': {
        'success': fields.Boolean(description='Indicates if the request was successful', example=False),
        'message': fields.String(description='Error message for internal server errors', example="Internal Server Error")
    }
}

def register_global_models_to_namespace(ns: Namespace):
    """Register global models with a namespace and return them for use in responses."""
    registered = {}
    for model_name, model_fields in models.items():
        registered[model_name] = ns.model(model_name, model_fields)
    return registered

def register_global_models(api: Api):
    """Register global models with the API for use across all namespaces."""
    for model_name, model_fields in models.items():
        if model_name not in api.models:
            api.models[model_name] = api.model(model_name, model_fields)


