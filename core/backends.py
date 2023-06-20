from django.contrib.auth.password_validation import (
    UserAttributeSimilarityValidator,
    MinimumLengthValidator,
    CommonPasswordValidator,
    NumericPasswordValidator,
)
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.forms import ValidationError

UserModel = get_user_model()


class ExtendedUserModelBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        # if username is None:
        #     username = kwargs.get(UserModel.USERNAME_FIELD,
        #                           kwargs.get(UserModel.EMAIL_FIELD))
        # if username is None or password is None:
        #     return
        try:
            user = UserModel._default_manager.get(Q(email__iexact=username))

        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:

            if user.check_password(password) and self.user_can_authenticate(user):
                return user

            # if not user.is_active:
            # raise forms.ValidationError('User is inactive.')


# This is a possible code block for django settings to enforce password requirements
# Based on the information from  and

# Import the built-in password validators

# Define a custom password validator that checks for at least one uppercase character

class UppercaseCharacterValidator:
    def validate(self, password, user=None):
        if not any(char.isupper() for char in password):
            raise ValidationError(
                "The password must contain at least one uppercase character.",
                code="password_no_upper",
            )

    def get_help_text(self):
        return "Your password must contain at least one uppercase character."

# Define a custom password validator that checks for at least one special character


class SpecialCharacterValidator:
    def validate(self, password, user=None):
        # Define a list of special characters
        special_characters = "!@#$%^&*()-_=+[]{};:,.<>/?\\|`~"
        if not any(char in special_characters for char in password):
            raise ValidationError(
                "The password must contain at least one special character.",
                code="password_no_special",
            )

    def get_help_text(self):
        return "Your password must contain at least one special character."

# Define a custom password validator that checks for at least one number


class NumberValidator:
    def validate(self, password, user=None):
        if not any(char.isdigit() for char in password):
            raise ValidationError(
                "The password must contain at least one number.",
                code="password_no_number",
            )

    def get_help_text(self):
        return "Your password must contain at least one number."
