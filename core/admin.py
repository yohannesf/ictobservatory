#from authtools.admin import NamedUserAdmin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
# Register your models here.
from django.utils.crypto import get_random_string
from django.contrib.auth.forms import PasswordResetForm
from django.utils.translation import gettext_lazy as _


from .models import SystemUser
from .forms import UserCreationForm, UserChangeForm


class SystemUserInline(admin.StackedInline):
    model = SystemUser
    can_delete = False
    verbose_name_plural = 'System Users'


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (
        #(None, {"fields": ("password",)}),
        (_("Personal info"), {
         "fields": ("first_name", "last_name", "email", "password")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    # "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            'description': (
                "Enter the new user's First Name, Last Name, and email address and click save."
                " The user will be emailed a link allowing them to login to"
                " the site and set their password."
            ),
            'fields': ('email', 'first_name', 'last_name'),
        }),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ('Password', {
            'description': "Optionally, you may set the user's password here.",
            'fields': ('password1', 'password2'),
            'classes': ('collapse', 'collapse-closed'),
        }),
    )
    inlines = (SystemUserInline,)
    list_display = ['email', 'first_name', 'last_name', 'is_active',
                    'getUserGroup', 'getUserOrganisation', 'getUserMemberState', 'getUserRole']

    ordering = ('email',)

    def save_model(self, request, obj, form, change):
        if not change and (not form.cleaned_data['password1'] or not obj.has_usable_password()):
            # Django's PasswordResetForm won't let us reset an unusable
            # password. We set it above super() so we don't have to save twice.
            obj.set_password(get_random_string(12))
            reset_password = True
        else:
            reset_password = False

        super(UserAdmin, self).save_model(request, obj, form, change)

        if reset_password:
            reset_form = PasswordResetForm({'email': obj.email})
            assert reset_form.is_valid()
            reset_form.save(
                request=request,
                # use_https=request.is_secure(),
                subject_template_name='registration/account_creation_subject.txt',
                email_template_name='registration/account_creation_email.html',
            )

    # add_fieldsets = (
    #     (
    #         None,
    #         {
    #             "classes": ("wide",),
    #             "fields": ("username", 'email', 'first_name', 'last_name', "password1", "password2"),
    #         },
    #     ),
    # )
    # inlines = (SystemUserInline,)
    # list_display = ['first_name', 'last_name',
    #                 'username', 'email', 'getUserGroup', 'getUserOrganisation', 'getUserMemberState']


    # Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
