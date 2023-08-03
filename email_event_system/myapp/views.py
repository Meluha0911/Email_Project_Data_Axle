from django.core.mail import send_mail
from django.views import View
from django.http import JsonResponse
from .models import Event, EmailTemplate, Employee, EmailLog
from django.utils import timezone

class SendEmailsView(View):
    def get(self, request):
        # Get the current date
        current_date = timezone.now().date()

        # Retrieve events for the current date
        events = Event.objects.filter(event_date=current_date)

        # Check if there are no events for the current date
        if not events.exists():
            # Log that no events are scheduled for the current period
            # You can add the logging logic here or create a separate table for it
            return JsonResponse({'message': 'No events scheduled for today.'})

        # Process each event and send emails
        for event in events:
            try:
                # Get the event details
                event_type = event.event_type
                event_date = event.event_date

                # Get the corresponding email template
                template = EmailTemplate.objects.get(event_type=event_type)

                # Get all employees for the event date
                employees = Employee.objects.filter(event__event_date=event_date)

                # Send personalized emails to employees
                for employee in employees:
                    # Populate email template with event-specific content
                    email_content = template.template_content.format(
                        employee_name=employee.name,
                        event_type=event_type,
                        event_date=event_date
                    )

                    # Send the email
                    send_mail(
                        subject='Event Reminder',
                        message=email_content,
                        from_email='noreply@example.com',
                        recipient_list=[employee.email],
                        fail_silently=False,
                    )

                    # Log successful email delivery
                    EmailLog.objects.create(
                        employee=employee,
                        event=event,
                        status='Success',
                    )

            except Exception as e:
                # Log the error and continue with the next scheduled email
                EmailLog.objects.create(
                    employee=employee,
                    event=event,
                    status='Error',
                    error_message=str(e)
                )
                continue

        return JsonResponse({'message': 'Emails sent successfully.'})
