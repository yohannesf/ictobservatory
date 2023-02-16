

from django.conf import settings
from notifications.models import Notification
from django.db.models import Count
from core.models import User
from django.core.mail import send_mail


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
