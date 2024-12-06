from django.db import models
from django.contrib.auth.models import User

# Model for tracking calories
class CalorieLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='calorie_logs'
    )  # Link to the user who owns this log
    date = models.DateField()  # Date of the calorie log
    food_item = models.CharField(max_length=100, blank=True, null=True)  # Optional food item description
    calories = models.PositiveIntegerField()  # Number of calories consumed
    date_logged = models.DateTimeField(auto_now_add=True)  # Automatically log the creation timestamp

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.calories} kcal"


# Model for appointments
class WTAppointment(models.Model):
    name = models.CharField(max_length=100)
    appointment_date = models.DateTimeField()
    description = models.TextField(blank=True, null=True)  # Optional field
    status = models.CharField(max_length=50, default='Pending')

    def __str__(self):
        return f"{self.name} - {self.appointment_date}"

# class Appointment(models.Model):
#     name = models.CharField(max_length=100)
#     appointment_date = models.DateTimeField()
#     description = models.TextField()
#     status = models.CharField(max_length=20)

    # def __str__(self):
    #     return f"Appointment with {self.name} on {self.appointment_date}"

class WT_appointment(models.Model):
    name = models.CharField(max_length=255)
    appointment_date = models.DateTimeField()
    description = models.TextField()
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Completed', 'Completed')])

    def __str__(self):
        return self.name

class Appointment(models.Model):
    name = models.CharField(max_length=255)
    appointment_date = models.DateField()
    description = models.TextField()
    status = models.CharField(max_length=100, choices=[('Scheduled', 'Scheduled'), ('Completed', 'Completed')])

    def __str__(self):
        return self.name