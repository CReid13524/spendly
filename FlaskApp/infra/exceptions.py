
from flask import current_app, Flask
from flask_restx import Api, fields
from http import HTTPStatus

def register_error_handlers(app: Flask, api: Api):
    @app.errorhandler(AppError)
    def handle_app_error(e: Exception):
        """Handle custom application errors."""
        return {
            "success": False,
            "message": str(e) or e.message
        }, getattr(e, 'status_code', HTTPStatus.BAD_REQUEST)

    @app.errorhandler(Exception)
    def handle_unexpected_error(e: Exception):
        """Handle uncaught exceptions, log and return generic error."""
        current_app.logger.exception(e)
        message = "Internal Server Error" if app.config.get('FLASK_ENVIRONMENT') == 'production' else f"DEBUG: {str(e)}"
        return {
            "success": False,
            "message": message
        }, HTTPStatus.INTERNAL_SERVER_ERROR

class AppError(Exception):
    """Use this as the base class for all custom exceptions in the application."""
    status_code = HTTPStatus.BAD_REQUEST

class NotFound(AppError):
    """Resource not found."""
    status_code = HTTPStatus.NOT_FOUND

class ValidationError(AppError):
    """Input validation failed."""
    status_code = HTTPStatus.BAD_REQUEST

class Unauthorized(AppError):
    """User is not authenticated to access the resource."""
    status_code = HTTPStatus.UNAUTHORIZED
    message = "Authentication required"
