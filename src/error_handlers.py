from flask import jsonify
from src.validation import ValidationError

def register_error_handlers(app):
    """Register error handlers for the Flask application"""
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle custom validation errors"""
        response = jsonify({
            'error': 'Validation Error',
            'message': error.message
        })
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 errors"""
        response = jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        })
        response.status_code = 404
        return response
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Handle 405 errors"""
        response = jsonify({
            'error': 'Method Not Allowed',
            'message': 'The method is not allowed for the requested URL'
        })
        response.status_code = 405
        return response
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle 500 errors"""
        response = jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        })
        response.status_code = 500
        return response
    
    @app.errorhandler(400)
    def handle_bad_request(error):
        """Handle 400 errors"""
        response = jsonify({
            'error': 'Bad Request',
            'message': 'The request could not be understood or was missing required parameters'
        })
        response.status_code = 400
        return response
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handle any unexpected errors"""
        # Log the error for debugging
        app.logger.error(f'Unexpected error: {str(error)}')
        
        response = jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        })
        response.status_code = 500
        return response