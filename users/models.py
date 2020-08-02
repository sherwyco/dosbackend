from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from eventtools.models import BaseEvent, BaseOccurrence
import uuid


class CustomUser(AbstractUser):
    user_types = (
        ('Individual', 'Individual'),
        ('Bulk', 'Bulk'),
        ('Commercial', 'Commercial'),
        ('Industrial', 'Industrial')
    )
    email = models.EmailField(blank=False, max_length=254, verbose_name="email address")
    type = models.CharField(choices=user_types, max_length=100, default='Individual')
    USERNAME_FIELD = "username"   # e.g: "username", "email"
    EMAIL_FIELD = "email"         # e.g: "email", "primary_email"
    phone_number = PhoneNumberField(blank=True, default=None, null=True, help_text='e.g +1 123 234 5678')


class PickUpInfo(BaseEvent):
    bin_types = (
        ('Compost', 'Compost'),
        ('Landfill', 'Landfill'),
        ('Wood', 'Wood'),
        ('Metal', 'Metal'),
        ('Paper/Cardboard', 'Paper/Cardboard'),
        ('Plastic Wrap', 'Plastic Wrap'),
        ('Plastic Bottles/Containers', 'Plastic Bottles/Containers'),
        ('Glass Bottles/Containers', 'Glass Bottles/Containers'),
        ('Aluminum Cans/Containers', 'Aluminum Cans/Containers'),
        ('E-waste', 'E-waste')
    )
    bin_type = models.CharField(choices=bin_types, max_length=255, null=False, blank=False)
    lbs = models.FloatField(null=False, blank=False, default=0.0)
    instructions = models.CharField(max_length=250, blank=True)

    def __str__(self):
        return '%d: %s' % (self.pk, self.bin_type)


class Schedule(BaseOccurrence):
    user = models.ForeignKey(CustomUser, null=False, blank=False, on_delete=models.CASCADE)
    event = models.ForeignKey(PickUpInfo, on_delete=models.CASCADE)

    def next(self):
        next_date = self.next_occurrence()
        return next_date[0] if next_date else None


class Address(models.Model):
    user = models.ForeignKey(CustomUser, blank=False, null=False, on_delete=models.CASCADE)
    street_name = models.CharField(max_length=1024, null=False, blank=False)
    city = models.CharField(max_length=1024)
    state = models.CharField(max_length=2, blank=True)
    zip_code = models.CharField(max_length=12, null=False, blank=False)
    country = models.CharField(max_length=3)

    def get_full_address(self):
        if self.state:
            return '%s, %s, %s, %s, %s' % (self.street_name, self.zip_code, self.city, self.state, self.country)
        else:
            return '%s, %s, %s, %s' % (self.street_name, self.zip_code, self.city, self.country)


class UserSettings(models.Model):
    user = models.ForeignKey(CustomUser, null=False, blank=False, on_delete=models.CASCADE)
    reminder = models.BooleanField('Remind me when a pickup is scheduled for the following day', default=False)
    notify = models.BooleanField('Notify me when a DoS employee has picked up my bin(s) for a pickup', default=False)
    seen = models.BooleanField(default=False)


class UserNotification(models.Model):
    class Type(models.IntegerChoices):
        ERROR = 0
        SUCCESS = 1
        WARNING = 2
        INFO = 3
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, null=False, blank=False, on_delete=models.CASCADE)
    notification_type = models.IntegerField(choices=Type.choices, default=3)
    message = models.TextField(null=False, blank=False)
