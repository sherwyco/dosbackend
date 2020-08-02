from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
from django.utils import timezone
from django.contrib import messages


class CustomUserAdmin(UserAdmin):
    model = CustomUser

    fieldsets = UserAdmin.fieldsets + (
            (None, {'fields': ('type', 'phone_number',)}),
    )


def complete_pickup(modeladmin, request, queryset):
    """ this will send notification to user's about their scheduled pickup """
    now = timezone.now()
    for obj in queryset:
        if obj.next_occurrence()[0] <= now:
            notify = UserNotification(user=obj.user, notification_type=1,
                                      message='Pick up no: %s completed!' % obj.event.id)
            notify.save()
            return messages.add_message(request, messages.SUCCESS, 'Notification sent to User(s)!')
        else:
            return messages.add_message(request, messages.ERROR, 'Pickup at %s is still far away!' % obj.start)


class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'event', 'start', 'end', 'next', 'repeat', 'repeat_until']
    actions = [complete_pickup]


class PickUpInfoAdmin(admin.ModelAdmin):
    list_display = ['pk', 'bin_type', 'lbs', 'instructions']


class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'street_name', 'state', 'zip_code', 'city']


class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'notification_type', 'message']


class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'reminder', 'notify']


admin.site.register(UserSettings, UserSettingsAdmin)
admin.site.register(UserNotification, UserNotificationAdmin)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(PickUpInfo, PickUpInfoAdmin)
admin.site.register(CustomUser, CustomUserAdmin)