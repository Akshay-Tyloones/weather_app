import requests
from jose import jwt
from django.http import JsonResponse
from .utils import format_api_response
from dotenv import load_dotenv
import os
load_dotenv()

class TokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        access_token = request.headers.get('Authorization')
        if access_token:
            access_token = access_token.split(' ')[1]
        protected_urls = [
                    {'path': '/get-image/', 'method': 'GET'},
                    {'path': '/add-to-favourite/', 'method': 'POST'},
                    {'path': '/upload/', 'method':'POST'},
                ]
        for url_data in protected_urls:
            if request.path == url_data['path'] and request.method == url_data['method']:
                decoded_token = self.validate_token(access_token)
                if decoded_token:
                    print('token is valid:', decoded_token)
                    cognito_id = decoded_token['sub']
                    print('cognito->', cognito_id)
                    request.cognito_id = cognito_id
                else:
                    print('token is not valid')
                    response_data = format_api_response(success=False, message='token is not valid')
                    return JsonResponse(response_data)
        return self.get_response(request)

    def validate_token(self, access_token):
        url = 'https://cognito-idp.ap-south-1.amazonaws.com/ap-south-1_XIzhTBXNy/.well-known/jwks.json'
        response = requests.get(url)
        data = response.json()
        # rsa_key = jwks_data['keys'][1]

        try:
            decoded_token = jwt.decode(
                access_token,
                data,
                algorithms=['RS256'],
                audience=os.getenv('CLIENT_ID'),    
            )
            return decoded_token
        except jwt.ExpiredSignatureError as e:
            response_data = format_api_response(success=False, message='token expired', error=str(e))
            return JsonResponse(response_data)
        except jwt.JWTError:
            response_data = format_api_response(success=False, message='invalid token', error=str(e))
            return JsonResponse(response_data)
        except Exception as e:
            response_data = format_api_response(success=False, message='error occur', error=str(e))
            return JsonResponse(response_data)
        



       
