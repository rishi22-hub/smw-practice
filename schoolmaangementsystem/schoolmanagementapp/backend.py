from django.contrib.auth.backends import ModelBackend
from .models import *
class PrincipalBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            print("inside authenticate")
            user = UserCredentials.objects.get(email=email)
            if user.check_password(password):
                print("authenticated")
                return user
        except UserCredentials.DoesNotExist:
            return None
