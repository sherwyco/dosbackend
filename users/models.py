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

    def save(self, *args, **kwargs):
        created = self.pk is None
        super(CustomUser, self).save(*args, **kwargs)
        if created:
            user_settings = UserSettings(user=self)
            user_settings.save()


class PickUpInfo(models.Model):
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
    user = models.ForeignKey(CustomUser, null=False, blank=False, on_delete=models.CASCADE)
    bin_type = models.CharField(choices=bin_types, max_length=255, blank=False)
    lbs = models.FloatField(null=False, blank=False, default=0.0)
    instructions = models.CharField(max_length=250, blank=True)

    def __str__(self):
        return '%s: %s' % (self.user, self.bin_type)


class CompletedPickUp(models.Model):
    user = models.ForeignKey(CustomUser, null=False, blank=False, on_delete=models.CASCADE)
    pick_up_info = models.ForeignKey(PickUpInfo, null=False, blank=False, on_delete=models.CASCADE)
    pick_up_date = models.DateTimeField(null=False, blank=False)

    def __str__(self):
        return '%s: date picked up: %s' % (self.pick_up_info, self.pick_up_date)


class Event(BaseEvent):
    info = models.ForeignKey(PickUpInfo, null=False, blank=False, on_delete=models.CASCADE)

    def __str__(self):
        return '%s: %s' % (self.info.user.username, self.info.bin_type)


class Schedule(BaseOccurrence):
    user = models.ForeignKey(CustomUser, null=False, blank=False, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, null=False, blank=False, on_delete=models.CASCADE)

    def next(self):
        next_date = self.next_occurrence()
        return next_date[0] if next_date else None

    def get_event_id(self):
        return self.event.pk


class Address(models.Model):
    user = models.OneToOneField(CustomUser, blank=False, on_delete=models.CASCADE)
    street_name = models.CharField(max_length=1024, blank=False)
    city = models.CharField(max_length=189, blank=False)
    state = models.CharField(max_length=189, blank=False)
    zip_code = models.CharField(max_length=18, blank=False)
    country = models.CharField(max_length=90, blank=False)

    def get_full_address(self):
        if self.state:
            return '%s, %s, %s, %s, %s' % (self.street_name, self.zip_code, self.city, self.state, self.country)


class UserSettings(models.Model):
    user = models.OneToOneField(CustomUser, null=False, blank=False, on_delete=models.CASCADE)
    reminder = models.BooleanField('Remind me when a pickup is scheduled for the following day', default=False)
    notify = models.BooleanField('Notify me when a DoS employee has picked up my bin(s) for a pickup', default=False)


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
    seen = models.BooleanField(default=False)
    created_date = models.DateField(auto_now_add=True)