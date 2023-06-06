
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django import forms
from .models import User


from django.utils.translation import gettext as _

from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserChangeForm as DjangoUserChangeForm
from django.contrib.auth import get_user_model, password_validation

from django import forms
# from authtools.forms import UserCreationForm

from django import forms
from .models import User


User = get_user_model()


class UserCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """

    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
        'duplicate_username': _("A user with that %(username)s already exists."),
    }

    password1 = forms.CharField(
        label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
                                widget=forms.PasswordInput,
                                help_text=_("Enter the same password as above,"
                                            " for verification."))

    password1.required = False
    password2.required = False

    class Meta:
        model = User
        fields = (User.USERNAME_FIELD,) + \
            tuple(User.REQUIRED_FIELDS)  # (User.USERNAME_FIELD,) +

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)

        self.fields['password1'].widget.attrs['autocomplete'] = 'off'
        self.fields['password2'].widget.attrs['autocomplete'] = 'off'

        # def validate_uniqueness_of_username_field(value):
        #     # Since User.username is unique, this check is redundant,
        #     # but it sets a nicer error message than the ORM. See #13147.
        #     try:
        #         User._default_manager.get_by_natural_key(value)
        #     except User.DoesNotExist:
        #         return value
        #     raise forms.ValidationError(self.error_messages['duplicate_username'] % {
        #         'username': User.USERNAME_FIELD,
        #     })

        # self.fields[User.USERNAME_FIELD].validators.append(
        #     validate_uniqueness_of_username_field)

    def clean_password2(self):
        '''Check that the two password entries match'''
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'])
        return password2

    def _post_clean(self):
        super(UserCreationForm, self)._post_clean()
        ''' Validate the password after self.instance is updated with form data by super().'''
        password = self.cleaned_data.get('password2')
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except forms.ValidationError as error:
                self.add_error('password2', error)

    def save(self, commit=True):
        ''' Save the provided password in hashed format'''
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(DjangoUserChangeForm):
    is_superuser = forms.BooleanField(
        label='Superuser Status', help_text='Designates that this user has all permissions without explicitly assigning them.', initial=False, required=False)
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_(
            "Raw passwords are not stored, so there is no way to see this "
            "user’s password, but you can change the password using "
            '<a href="{}">this form</a>.'
        ),
    )

    class Meta:
        model = User
        fields = "__all__"

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            password = self.fields.get("password")

            if password:
                password.help_text = password.help_text.format("../password/")
            user_permissions = self.fields.get("user_permissions")
            if user_permissions:
                user_permissions.queryset = user_permissions.queryset.select_related(
                    "content_type"
                )


# class LoginForm(AuthenticationForm):
#     print("here")

#     def clean(self):
#         username = self.cleaned_data.get('username')
#         password = self.cleaned_data.get('password')

#         if username is not None and password:
#             self.user_cache = authenticate(
#                 self.request, username=username, password=password)
#             if self.user_cache is None:
#                 try:
#                     user_temp = User.objects.get(username=username)
#                 except:
#                     user_temp = None

#                 if user_temp is not None:
#                     self.confirm_login_allowed(user_temp)
#                 else:
#                     raise forms.ValidationError(
#                         self.error_messages['invalid_login'],
#                         code='invalid_login',
#                         params={'username': self.username_field.verbose_name},
#                     )

#         return self.cleaned_data


# class LoginForm(forms.Form):
#     username = forms.CharField()
#     password = forms.CharField(widget=forms.PasswordInput)

#     def clean(self):
#         username = self.cleaned_data.get('username')
#         password = self.cleaned_data.get('password')
#         user = authenticate(username=username, password=password)
#         if user is None:
#             raise forms.ValidationError('Invalid username or password.')
#         elif not user.is_active:
#             raise forms.ValidationError('User is inactive.')
#         return self.cleaned_data
