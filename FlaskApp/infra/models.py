from flask_restx import fields, Namespace, Api

models = {
    'RequireAuth': {
        'success': fields.Boolean(description='Indicates if the request was successful', example=False),
        'message': fields.String(description='Error message if authentication fails', example="Authentication required")
    },
    'InternalServerError': {
        'success': fields.Boolean(description='Indicates if the request was successful', example=False),
        'message': fields.String(description='Error message for internal server errors', example="Internal Server Error")
    },
    'BadRequest': {
        'success': fields.Boolean(description='Indicates if the request was successful', example=False),
        'message': fields.String(description='Error message for bad requests', example="Bad Request")
    },
    'OK': {
        'success': fields.Boolean(description='Indicates if the request was successful', example=True)
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


# Custom boolean parser for query params
def parse_bool(val):
    if isinstance(val, bool):
        return val
    if val is None:
        return None
    val = str(val).strip().lower()
    if val in ('true'):
        return True
    if val in ('false'):
        return False
    raise ValueError(f"Invalid boolean value: {val}")


# Parser for fields that allow boolean (existence) or string/UUID (exact match)
def parse_bool_or_other(val, type):
    if val is None:
        return None
    # Try boolean first
    try:
        return parse_bool(val)
    except Exception:
        pass
    return type(val)


class NullableString(fields.String):
    __schema_type__ = ['string', 'null']
    __schema_example__ = 'nullable string'


class NullableFloat(fields.Float):
    __schema_type__ = ['number', 'null']
    __schema_example__ = 'nullable number'
