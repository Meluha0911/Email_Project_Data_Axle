from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import date
from .models import Event, EmailTemplate, Employee, EmailLog


class EmailSendingTestCase(TestCase):
    def setUp(self):
        # Create test data for the database

        # Create test events
        self.event1 = Event.objects.create(event_type='Birthday', event_date=date.today())
        self.event2 = Event.objects.create(event_type='Work Anniversary', event_date=date.today())

        # Create test email templates
        self.template1 = EmailTemplate.objects.create(event_type='Birthday',
                                                      template_content='Happy Birthday, {employee_name}!')
        self.template2 = EmailTemplate.objects.create(event_type='Work Anniversary',
                                                      template_content='Happy Work Anniversary, {employee_name}!')

        # Create test employees
        self.employee1 = Employee.objects.create(name='John Doe', email='john@example.com')
        self.employee2 = Employee.objects.create(name='Jane Smith', email='jane@example.com')

    def test_email_sending(self):
        # Test the email sending functionality
        client = Client()

        # Send the emails by making a GET request to the endpoint
        response = client.get(reverse('send_emails'))

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Verify that the emails are sent successfully by checking the EmailLog
        email_logs = EmailLog.objects.all()
        self.assertEqual(len(email_logs), 2)  # Two employees should have received emails

        for log in email_logs:
            self.assertEqual(log.status, 'Success')  # All emails should have been sent successfully

    def test_no_events_today(self):
        # Test when there are no events for the current date
        client = Client()

        # Set the event date to a future date
        future_date = date.today() + timezone.timedelta(days=10)
        Event.objects.create(event_type='Birthday', event_date=future_date)

        # Send the emails by making a GET request to the endpoint
        response = client.get(reverse('send_emails'))

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Verify that no emails were sent because there are no events today
        email_logs = EmailLog.objects.all()
        self.assertEqual(len(email_logs), 0)  # No emails should have been sent

    def test_email_sending_errors(self):
        # Test the system behavior when there are errors in sending emails
        # To simulate an error, we will set an incorrect email address for an employee
        client = Client()
        self.employee1.email = 'invalid-email-format'  # Invalid email format
        self.employee1.save()

        # Send the emails by making a GET request to the endpoint
        response = client.get(reverse('send_emails'))

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Verify that the email for employee1 failed and an error message is logged
        email_logs = EmailLog.objects.all()
        self.assertEqual(len(email_logs), 1)  # Only one email should have been attempted
        self.assertEqual(email_logs[0].status, 'Error')  # The email should have failed
        self.assertIsNotNone(email_logs[0].error_message)  # An error message should be logged

    def test_last_successful_execution_time(self):
        # Test storing the last successful execution time for subsequent runs
        client = Client()

        # Send the emails by making a GET request to the endpoint
        response = client.get(reverse('send_emails'))

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Verify that the last successful execution time is stored in the database
        last_execution_time = timezone.now()
        email_logs = EmailLog.objects.all()
        for log in email_logs:
            last_execution_time = max(last_execution_time, log.sent_at)

        # Assuming that the last execution time was stored in a separate model, you can perform assertions like this:
        # self.assertEqual(LastExecutionTimeModel.objects.last_execution_time, last_execution_time)


