from django.db import models
from django.contrib.auth.models import AbstractUser


class UserDetails(AbstractUser):
    cognito_user = models.CharField(default="hello", max_length=100)
    is_verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=10, null=True)
    image_url = models.URLField(default=None, null=True)

class FavouriteCity(models.Model):
    user_id = models.ForeignKey(UserDetails,on_delete=models.CASCADE)
    city_name = models.CharField(max_length=50, null=True)


    def __str__(self) -> str:
        return self






