from django.db import models

class Event(models.Model):
    event_type = models.CharField(max_length=50)
    event_date = models.DateField()

class EmailTemplate(models.Model):
    event_type = models.CharField(max_length=50)
    template_content = models.TextField()

class Employee(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

class EmailLog(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    status = models.CharField(max_length=20)
    error_message = models.TextField(null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
