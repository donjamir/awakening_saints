from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class EmailAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, email=None, password=None, **kwargs):
        identifier = email or username  # admin will send "username", even if it's email

        try:
            user = UserModel.objects.get(email=identifier)
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
