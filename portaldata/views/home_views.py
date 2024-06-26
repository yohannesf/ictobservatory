from django.db.models import Q
from django.contrib import messages
from django.core.mail import send_mail, send_mass_mail
from django.conf import settings
from notifications.signals import notify
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from core.models import SystemUser, User
from core.sharedfunctions import get_published_years
from portaldata.cron import reporting_period_open

from portaldata.forms.send_message_form import SendMessageFormForAdmins, SendMessageFormForMS
from portaldata.views.admin_views import data_entry_progress_admin_dashboard

from portaldata.views.indicator_data_views import (
    send_message_copy_to_self_ms,
    send_message_copy_to_self_org,
    update_currency_indicators_to_usd,
)
from ..models import Indicator, IndicatorData, MemberState
from core.decorators import group_required


@login_required
@group_required("Member State", "Organisation", "SADC", "Admin")
def index(request):
    """Backend Home Page (a landing page when user is logged in)"""

    # TO DO -> to be replaced by a button on the backend for admins with year selection dropdown

    context = {}

    if (request.user.is_superuser or request.user.is_sadc):
        if get_published_years():
            years_qs = get_published_years()
            [update_currency_indicators_to_usd(i) for i in years_qs]

        context = {'progress': data_entry_progress_admin_dashboard()}

    return render(request, "portaldata/index.html", context=context)


def send_emails(recipient_list, subject, message, mass=False):
    email_from = settings.EMAIL_HOST_USER

    if mass:

        mass_email = [(subject, message, email_from, [recipient])
                      for recipient in recipient_list]

        send_mass_mail(mass_email)
    else:
        # pass

        send_mail(subject, message, email_from, recipient_list)


def send_reporting_period_open_notification():

    try:

        users = []  # Users to be notified
        emails = []  # email addresses of users
        admin = ''

        subject = "Reporting Period Open"
        message = '''This is to inform you that data entry period starts today. 

Please sign in to SADC ICT Observatory to start entering data.

SADC Secretariat'''

        admins = User.objects.filter(is_superuser=True)

        if admins:
            admin = admins.first()

        all_ms = list(MemberState.objects.filter(
            memberstate_status=True).values_list('id', flat=True).order_by('member_state'))

        users = list(User.objects.filter(
            systemuser__user_member_state__in=list(all_ms)).exclude(is_active=False))

        if users:
            # send notification
            notify.send(admin, recipient=users,
                        verb=subject, description=message,)
            try:
                # Append email addresses of users to a list - to pass it to the send_emails function
                [emails.append(i.email) for i in users]
            except:
                pass

        if emails:
            emails.append(admin.email)

            send_emails(emails, subject=subject,
                        message=message, mass=True)

    except:
        pass


@login_required
@staff_member_required
def send_message_by_admins(request):
    """Send Message, system wide"""

    form = SendMessageFormForAdmins(request.POST or None)

    if request.method == "POST":

        users = []  # Users to be notified
        emails = []  # email addresses of users

        ms = request.POST.getlist('memberstate_filter_field')
        subject = request.POST['subject']
        message = request.POST['message']

        if form.is_valid():

            if ms and ms != ['all'] and 'all' not in ms:
                users = list(User.objects.filter(
                    systemuser__user_member_state__in=list(ms)).exclude(is_active=False))

            if ms and (ms == ['all'] or 'all' in ms):
                all_ms = list(MemberState.objects.filter(
                    memberstate_status=True).values_list('id', flat=True).order_by('member_state'))

                users = list(User.objects.filter(
                    systemuser__user_member_state__in=list(all_ms)).exclude(is_active=False))

            if users:
                # send notification
                notify.send(request.user, recipient=users,
                            verb=subject, description=message,)
                try:
                    # Append email addresses of users to a list - to pass it to the send_emails function
                    [emails.append(i.email) for i in users]
                except:
                    pass

            if emails:
                emails.append(request.user.email)
                send_emails(emails, subject=subject,
                            message=message, mass=True)
            messages.success(request, "Message Sent Successfully")
            form = SendMessageFormForAdmins()

            # return render(request, "portaldata/send_message.html", {"form": form})

    context = {"form": form}

    return render(request, "portaldata/send_message_by_admin.html", context=context)


@login_required
def send_message_by_ms(request):
    """Send Messages to SADC"""

    form = SendMessageFormForMS(request.POST or None)

    if request.method == "POST":

        users = []  # Users to be notified
        emails = []  # email addresses of users

        subject = request.POST['subject']
        message = request.POST['message']

        if form.is_valid():

            # Get users who are in the SADC group (without necessarily being superusers)
            sadc = list(
                SystemUser.objects.filter(
                    user_organisation__organisation_name__iexact="SADC"
                ).values_list("user__id", flat=True)
            )

            if sadc:
                users = list(
                    User.objects.filter(Q(id__in=sadc) | Q(is_superuser=True))
                    .distinct()
                    .order_by()
                )
            else:
                users = list(User.objects.filter(
                    Q(is_superuser=True)).distinct().order_by())

            if users:
                # send notification
                notify.send(request.user, recipient=users,
                            verb=subject, description=message,)
                try:
                    # Append email addresses of users to a list - to pass it to the send_emails function
                    [emails.append(i.email) for i in users]
                except:
                    pass

            if emails:
                emails.append(request.user.email)
                send_emails(emails, subject=subject,
                            message=message, mass=False)
            messages.success(request, "Message Sent Successfully")
            form = SendMessageFormForMS()

            # return render(request, "portaldata/send_message.html", {"form": form})

    context = {"form": form}

    return render(request, "portaldata/send_message_by_ms.html", context=context)


@login_required
def documentation(request):
    return render(request, "portaldata/documentation.html")


def count_all_active_required_indicators():
    ind_count = Indicator.objects.filter(
        status="Active",
        required=True,
    ).count()
    return ind_count


def count_all_completed_required_indicators():
    ind_count = (
        IndicatorData.objects.filter(
            indicator__required=True,
        )
        .exclude(value_NA=False, value__exact="")
        .exclude(value_NA=False, value__isnull=True)
        .count()
    )
    return ind_count


def calculate_overall_progress():
    if count_all_active_required_indicators() == 0:
        return 0
    else:
        ind_progress = round(
            count_all_completed_required_indicators()
            / count_all_active_required_indicators()
            * 100
        )
        return ind_progress
