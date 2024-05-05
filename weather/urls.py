from django.urls import path 
from .views import  home, signin, signup, verify_email,add_to_favourite, upload_image, get_image_from_s3,invloke_lambda

urlpatterns = [
    path('', home, name = 'home'),
    path('signup/', signup, name='signup'),
    path('signin/', signin, name='signin'),
    path('verify-email/<str:email>/', verify_email, name='verify_email'),
    path('add-to-favourite/', add_to_favourite, name='add_to_favourite'),
    path('upload/', upload_image, name='upload-image'),
    path('get-image/', get_image_from_s3, name='get-image'),
    path('invoke-lambda/', invloke_lambda, name='invoke-lambda')


]