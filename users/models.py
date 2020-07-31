from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from eventtools.models import BaseEvent, BaseOccurrence


class CustomUser(AbstractUser, models.Model):
    user_types = (
        ('Individual', 'Individual'),
        ('Bulk', 'Bulk'),
        ('Commercial', 'Commercial'),
        ('Industrial', 'Industrial')
    )
    email = models.EmailField(blank=False, max_length=254, verbose_name="email address")
    type = models.CharField(choices=user_types, max_length=100, blank=True)
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
    instructions = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return '%d: %s' % (self.pk, self.bin_type)


class Schedule(BaseOccurrence):
    customer_id = models.ForeignKey(CustomUser, null=False, blank=False, on_delete=models.CASCADE)
    event = models.ForeignKey(PickUpInfo, on_delete=models.CASCADE)

    def first(self):
        return str(self.occurrence_data)

    def next(self):
        return str(self.next_occurrence(from_date=self.end, to_date=self.repeat_until))
