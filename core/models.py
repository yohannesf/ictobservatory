from django.contrib.auth.models import AbstractUser, AbstractBaseUser, Group, BaseUserManager
from django.db import models
from django.conf import settings
from django.forms import ValidationError
from portaldata.models import MemberState, Organisation
from django.dispatch import receiver
from django.db.models.signals import post_save


from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **kwargs):
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)

        if kwargs.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if kwargs.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        print("here")

        return self.create_user(email, password, **kwargs)

    def get_by_natural_key(self, email):
        normalized_email = self.normalize_email(email)
        return self.get(**{self.model.USERNAME_FIELD: normalized_email})


class AbstractEmailUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), max_length=255, unique=True)

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin '
                                               'site.'))
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        abstract = True
        ordering = ['email']

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

    def get_short_name(self):
        return self.email

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Sends an email to this User."""

        send_mail(subject, message, from_email, [self.email], **kwargs)


class User(AbstractEmailUser):

    def getSysUser(self):
        return SystemUser.objects.get(user=self)

    def is_organisation(self):

        if self.getSysUser().user_group.name == "Organisation":
            return True
        else:
            return False

    def is_memberstate(self):

        if self.getSysUser().user_group.name == "Member State":
            return True
        else:
            return False

    def is_sadc(self):

        if self.getSysUser().user_group.name == "SADC":
            return True
        else:
            return False

    def getUserOrganisation(self):
        return self.getSysUser().user_organisation

    def getUserMemberState(self):
        return self.getSysUser().user_member_state

    def getUserGroup(self):
        return self.getSysUser().user_group

    def __str__(self):
        return self.get_full_name()


class SystemUser(models.Model):
    '''
    ----------------------------
    SystemUsers model will be used to ensure the appropriate data entry form is served to the user based on identity
    For example, Member States will see data entry form with indicators assigned to them
    while Organizations (e.g. CRASA) will get a different data entry form that enables them to enter data for member states
    '''

    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)

    phone_number = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=150, blank=True)
    organisation_name = models.CharField(max_length=150, blank=True)
    user_group = models.ForeignKey(
        Group, on_delete=models.PROTECT, verbose_name='User Group')

    user_member_state = models.ForeignKey(
        MemberState, on_delete=models.PROTECT, null=True, blank=True, verbose_name='User Member State')
    user_organisation = models.ForeignKey(
        Organisation, on_delete=models.PROTECT, null=True, blank=True,  verbose_name='Organisation')

    def name(self):
        return f'{self.user.first_name} {self.user.last_name}'

    def email(self):
        return self.user.email

    def clean(self):
        super().clean()

        if self.user_member_state is None and self.user_organisation is None:
            if self.user_group.name != 'Admin' and self.user_group.name != 'SADC':
                raise ValidationError(
                    'Select either Member State or Organisation')
        if self.user_member_state is not None and self.user_organisation is not None:
            raise ValidationError(
                'A user can belong to either a memeber state or organisation')

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} ({self.user.email})'

    class Meta:
        ordering = ['user__first_name', 'user__last_name']
