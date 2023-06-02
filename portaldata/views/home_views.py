from django.db.models import Q
from django.contrib import messages
from django.core.mail import send_mail, send_mass_mail
from django.conf import settings
from notifications.signals import notify
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from core.models import SystemUser, User
from core.views import Get_Reporting_Year
from portaldata.forms.send_message_form import SendMessage_byAdmins, SendMessage_byMS

from portaldata.views.indicator_data_views import (
    SendNotification_to_self,
    SendNotification_to_self_orgs,
    update_currency_indicators_to_usd,
)
from ..models import Indicator, IndicatorData, MemberState


@login_required
def index(request):
    """Backend Home Page (a landing page when user is logged in)"""

    # TO DO -> to be replaced by a button on the backend for admins with year selection dropdown
    update_currency_indicators_to_usd("2022")

    return render(request, "portaldata/index.html")


def send_emails(recipient_list, subject, message, mass=False):
    email_from = settings.EMAIL_HOST_USER

    if mass:

        mass_email = [(subject, message, email_from, [recipient])
                      for recipient in recipient_list]

        # send_mass_mail(mass_email)
    else:
        pass

        #send_mail(subject, message, email_from, recipient_list)


@login_required
def send_message_by_admins(request):
    """Send Message, system wide"""

    form = SendMessage_byAdmins(request.POST or None)

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
            form = SendMessage_byAdmins()

            # return render(request, "portaldata/send_message.html", {"form": form})

    context = {"form": form}

    return render(request, "portaldata/send_message_by_admin.html", context=context)


@login_required
def send_message_by_ms(request):
    """Send Messages to SADC"""

    form = SendMessage_byMS(request.POST or None)

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
            form = SendMessage_byMS()

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
