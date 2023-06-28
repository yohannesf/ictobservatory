

import subprocess
import datetime
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


def backup_db():

    # This python code can be used to backup a postgres database given the host, user, password and dbname parameters. It also requires a directory to store the backup file. The code uses the subprocess module to run the pg_dump command and the datetime module to generate a timestamp for the backup file name. The code assumes that the pg_dump command is available in the system path.

    # Define the parameters for the database connection
    # host = "localhost"
    # user = "postgres"
    # password = "postgres"
    # dbname = "testdb"

    host = "localhost"
    user = "sadc"
    password = "AVNS_3c9d-bYqLniar99pFdH"
    dbname = "sadc"

    # Define the directory to store the backup file
    #backup_dir = "/home/user/backups"
    backup_dir = "/home/yfikre@sadc.int/backup"

    # Generate a timestamp for the backup file name
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    # Construct the backup file name
    backup_file = f"{backup_dir}/{dbname}_{timestamp}.sql"

    # Construct the pg_dump command
    pg_dump_cmd = f"pg_dump -h {host} -U {user} -w -F p {dbname} > {backup_file}"

    # Set the environment variable for the password
    env = {"PGPASSWORD": password}

    # Run the pg_dump command using subprocess
    subprocess.run(pg_dump_cmd, shell=True, env=env)

    # Print a message indicating success
    print(f"Backup completed. File saved as {backup_file}")
