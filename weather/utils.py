def format_api_response(success, data=None, message=None, error=None):
    response = {
        'success': success,
        'data': data if data is not None else {},
        'message': message if message is not None else 'null',
        'error': error if error is not None else 'null'
    }
    return response