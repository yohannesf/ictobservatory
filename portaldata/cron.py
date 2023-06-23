

from datetime import date
from django.conf import settings
from notifications.models import Notification
from django.db.models import Count
from core.models import User
from django.core.mail import send_mail

from portaldata.models import MemberState, ReportingPeriod


def reporting_period_open():
    from portaldata.views.home_views import send_reporting_period_open_notification

    reporting_start_date = ReportingPeriod.objects.filter(current=True)

    if reporting_start_date:

        start_date = reporting_start_date.first()

        if date.today() == start_date.reporting_start_date:

            send_reporting_period_open_notification()


def email_notifications():

    #notifications = Notification.objects.filter(emailed=False)

    subject = 'SADC ICT Observatory - Unread Notifications'
    email_from = settings.EMAIL_HOST_USER
    notifications = Notification.objects.filter(emailed=False)

    notifications = Notification.objects.filter(emailed=False).values(
        'recipient').annotate(total=Count('id')).order_by()

    for n in notifications:
        recipient = User.objects.get(id=n.get("recipient"))
        recipient_list = [recipient.email, ]

        message = f'''
Dear {recipient.get_full_name().title()}

You have {n.get("total")} unread notifications. Please log into your account to read.

SADC Secretariat
http://www.sadc.org
        '''

        print(recipient)
        print(message)
        #send_mail(subject, message, email_from, recipient_list)

    # Notification.objects.filter(emailed=False).update(emailed=True)

    # return HttpResponse("sent")
