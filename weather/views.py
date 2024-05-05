from .models import UserDetails, FavouriteCity
from django.http import HttpResponse
from django.conf import settings
from django.http import JsonResponse
from .utils import format_api_response
from dotenv import load_dotenv
import requests
import boto3
import json
import os
load_dotenv()



def home(request):
    city = request.GET.get("city", "indore")
    weather_url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid=a03a1b1193e5bff9dffc0e3297215f56'
    forcast_url = f'https://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&appid=a03a1b1193e5bff9dffc0e3297215f56&cnt=5'
    try:
        weather_response = requests.get(weather_url)
        forcast_response = requests.get(forcast_url)
        weather_data = weather_response.json()
        forcast_data = forcast_response.json()
        print(weather_data, forcast_data)
        weather_details = {
                'id' : int(weather_data['id']),
                'temperature' : int(weather_data['main']['temp']),
                'min_temperature' : int(weather_data['main']['temp_min']),
                'max_temperature' : int(weather_data['main']['temp_max']),
                'city' : weather_data['name'],
                'humidity' : int(weather_data['main']["humidity"]),
                'wind_speed' : int(weather_data["wind"]["speed"]),
                'description': weather_data['weather'][0]['description'],
                'icon' : weather_data['weather'][0]['icon'],
                'five_days_forcast' : forcast_data['list']
            }
        
        
        return JsonResponse(weather_details)

    except Exception as e:
         response_data = format_api_response(success=False,message="error occur",error=str(e))
         return JsonResponse(response_data)
    

def generate_tokens(email):
        cognito_client = boto3.client('cognito-idp', region_name='ap-south-1')
        params = {
            'AuthFlow': 'ADMIN_NO_SRP_AUTH',
            'ClientId':  settings.CLIENT_ID,
            'UserPoolId': settings.USER_POOL_ID,
            'AuthParameters': {
                'USERNAME': email,
                }
        }
        # Call AdminInitiateAuth method
        try:
            response = cognito_client.admin_initiate_auth(**params)
            tokens = response['AuthenticationResult']
            access_token = tokens['AccessToken']
            refresh_token = tokens['RefreshToken']
            print("Access Token:", access_token)
            print("Refresh Token:", refresh_token)
            # Use access token and refresh token
        except cognito_client.exceptions.NotAuthorizedException:
            print("Invalid username")
        except Exception as e:
            print("Error:", e)
            # Handle other errors
    
def signup(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        phone_number = data.get('phone_number')
        
        client = boto3.client('cognito-idp', region_name='ap-south-1')
        
        try:
            response = client.sign_up(
                ClientId=settings.CLIENT_ID,
                Username=email,  
                Password=password,
                UserAttributes=[
                    {
                        'Name': 'email',
                        'Value': email
                    },
                    {
                        'Name': 'name',
                        'Value': name
                    }
                ]
            )
            print('response->', response)
            cognito_id = response['UserSub']
            print('cognito_userid->', cognito_id)
           
            user = UserDetails.objects.create(
                username=name,
                cognito_user=cognito_id,
                email=email, 
                first_name=first_name,
                last_name=last_name,
                phone_number = phone_number
            )
            response_data = format_api_response(success=True, message="user registered successfully")
            return JsonResponse(response_data)
        except client.exceptions.UsernameExistsException as e:
            response_data = format_api_response(success=False, message="username already exists",error=str(e))
            return JsonResponse(response_data)
        except Exception as e:
            response_data = format_api_response(success=False ,error=str(e))
            return JsonResponse(response_data)
        
        


def verify_email(request, email):
    if request.method == 'POST':
        data = json.loads(request.body)
        verification_code = data.get('verification_code')

        cognito_client = boto3.client('cognito-idp', region_name='ap-south-1')

        try:
            response = cognito_client.confirm_sign_up(
                ClientId=settings.CLIENT_ID,
                Username=email,
                ConfirmationCode=verification_code
            )
            user = UserDetails.objects.get(email=email)
            user.is_verified = True
            user.save()
            print('response -> ' ,user.is_verified)

            response_data = format_api_response(success=True, message="verification success")
            return JsonResponse(response_data)  
        except cognito_client.exceptions.UserNotFoundException as e:
            response_data = format_api_response(success=False, message="user does not exist", error=str(e))
            return JsonResponse(response_data)
        except cognito_client.exceptions.CodeMismatchException as e:
            response_data = format_api_response(success=False, message="invalid verification code", error=str(e))
            return JsonResponse(response_data)
        except cognito_client.exceptions.NotAuthorizedException as e:
            response_data = format_api_response(success=False, message="user is already confirmed", error=str(e))
            return JsonResponse(response_data)
        except Exception as e:
            response_data = format_api_response(success=False, message="error occur", error=str(e))
            return JsonResponse(response_data)



def signin(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        email = data.get('email')
        password = data.get('password')


        client = boto3.client('cognito-idp', region_name='ap-south-1')
        try:
            response = client.initiate_auth(
                ClientId=settings.CLIENT_ID,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password
                }
            )
            print('response->', response)
            data = {'email' : email, 'password' : password}
            response_data = format_api_response(success=True, data=data, message='sign in successful')
            return JsonResponse(response_data)
        except client.exceptions.NotAuthorizedException as e:
            response_data = format_api_response(success=False, message='incorrect username or password',error=str(e))
            return JsonResponse(response_data)
        except client.exceptions.UserNotFoundException as e:
            response_data = format_api_response(success=False, message="user not found", error=str(e))
            return JsonResponse(response_data)
        


def add_to_favourite(request):

    cognito_id = request.cognito_id
    print('cognito_user_id->', cognito_id)
    # email = request.headers.get('Email')
    city_name = request.headers.get('City')

    if not cognito_id:
        response_data = format_api_response(success=False, message='email is required')
        return JsonResponse(response_data)
    elif not city_name:
        response_data = format_api_response(success=False, message='city name is required')
        return JsonResponse(response_data)

    
    try:
        user = UserDetails.objects.get(cognito_user=cognito_id)
    except UserDetails.DoesNotExist as e:
        data={'cognito_id' : cognito_id},
        response_data = format_api_response(success=False, data=data, message="user not found", error=str(e))
        return JsonResponse(response_data)
    
    #count number of city
    
    if FavouriteCity.objects.filter(user_id=user).count() >= 5:
        count_cities = FavouriteCity.objects.filter(user_id=user).count()
        data={'city_count': count_cities}
        response_data = format_api_response(success=False,data=data, message="maximum number of cities reached")
        return JsonResponse(response_data)
    
    #check already exist
    if FavouriteCity.objects.filter(user_id=user, city_name=city_name).exists():
        response_data = format_api_response(success=False, message="city already exists in favorites")
        return JsonResponse(response_data)
    #otherwise add in favourite
    FavouriteCity.objects.create(user_id=user, city_name=city_name)

    response_data = format_api_response(success=True, message="city added successfully")
    return JsonResponse(response_data)
    



def upload_image(request):
    # if request.method == 'POST' and request.FILES.get('image'):
    #     email = request.headers.get('email')
    if request.method == 'POST':
        
        cognito_id = request.cognito_id
        print('cognito_user_id->', cognito_id)
        # email = request.headers.get('email')
        image_file = request.FILES.get('image')

        try:
            user = UserDetails.objects.get(cognito_user=cognito_id)
        except UserDetails.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        # image_file = request.FILES['image']


        s3 = boto3.client('s3', 
                          aws_access_key_id=settings.ACCESS_KEY_ID, 
                          aws_secret_access_key=settings.SECRET_ACCESS_KEY
                        )
        bucket_name = os.getenv('S3_BUCKET_NAME')
        print(image_file, image_file.name)
        response = s3.upload_fileobj(image_file, bucket_name, image_file.name)
        print('s3response', response)
        # response = s3.put_object(Bucket=bucket_name, Key=image_file.name)
        # print('response->>>', response)
    
        url = image_file.name

        user.image_url = url
        user.save()

        return JsonResponse({'url': url}, status=201)

    return JsonResponse({'error': 'invalid request'}, status=400)






def get_image_from_s3(request):
    
    cognito_id = request.cognito_id
    print('cognito_user_id->', cognito_id)
    cloudfront_url = os.getenv('PRIFIX')

    # email = request.headers.get('email')

    try:
        user = UserDetails.objects.get(cognito_user=cognito_id)
    except UserDetails.DoesNotExist:
        response_data = format_api_response(success=False, message="user not found")
        return JsonResponse(response_data)
    
    favorites = FavouriteCity.objects.filter(user_id=user)
  
        
        
    favorite_cities = []
        
        
    for favorite in favorites:
        favorite_cities.append(favorite.city_name)
    image_url = user.image_url
    if image_url == 'null' or image_url == None:
        image_url = "https://cdn-icons-png.flaticon.com/512/149/149071.png"
    else:
        print('image_url->>>',image_url)
        image_url = f'{cloudfront_url}/{image_url}'
    

    user_info = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone_number': user.phone_number,
            'favorites_cities': favorite_cities,
            'image_url'  : image_url  
        }
    print('userdetails', user_info)
    
    response_data = format_api_response(success=True, data=user_info,message="data recive")

    return JsonResponse(response_data)


def invloke_lambda(request):

 try:
        aws_access_key_id = os.getenv('ACCESS_KEY_ID')
        aws_secret_access_key = os.getenv('SECRET_ACCESS_KEY')

        lambda_client = boto3.client('lambda', 
                                    region_name='ap-south-1', 
                                    aws_access_key_id=aws_access_key_id, 
                                    aws_secret_access_key=aws_secret_access_key)

        response = lambda_client.invoke(FunctionName= 'store_userinformation',
                                        InvocationType='RequestResponse', 
                                        Payload= json.dumps({'userId': 126,
                                                            'username': 'lalit',
                                                            'email': 'lalit@gmail.com'
                                                            }))
               

        if response['StatusCode'] == 200:
            print('response',response)
            response_payload = json.loads(response['Payload'].read())
            print('lambda_msg->', response_payload)
            response_data = format_api_response(success=True, message='lambda function invoked successfully')
            return JsonResponse(response_data)
        else:
            print("Invocation failed:", response['StatusCode'])
            response_data = format_api_response(success=True, message='Lambda function invocation failed')
            return JsonResponse({'error': 'Lambda function invocation failed'}, status=500)

 except Exception as e:
        print("Error:", e)
        response_data = format_api_response(success=False, message='error',error= str(e))
        return JsonResponse(response_data)
  






    





    

    
