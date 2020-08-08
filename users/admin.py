from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
from django.utils import timezone
from django.contrib import messages
from import_export.admin import ImportExportModelAdmin
from import_export import resources


class CustomUserAdmin(UserAdmin):
    model = CustomUser

    fieldsets = UserAdmin.fieldsets + (
            (None, {'fields': ('type', 'phone_number',)}),
    )


def complete_pickup(modeladmin, request, queryset):
    """ this will send notification to user's about their scheduled pickup """
    now = timezone.now()
    for obj in queryset:
        if obj.next_occurrence():
            # create object for completed pick up table
            CompletedPickUp.objects.create(user=CustomUser.objects.get(pk=obj.user.pk),
                                           pick_up_info=PickUpInfo.objects.get(pk=obj.event.info.pk),
                                           pick_up_date=now)
            if obj.next_occurrence()[0] <= now:
                notify = UserNotification(user=obj.user, notification_type=1,
                                          message='DOS has picked up bin no: %s!' % obj.event.info.id)
                notify.save()
                return messages.add_message(request, messages.SUCCESS, 'Notification sent to User(s)!')
            else:
                return messages.add_message(request, messages.ERROR, 'Pickup at %s is still far away!' % obj.start)
        else:
            return messages.add_message(request, messages.ERROR, 'Unable for pick up!')


class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'event', 'start', 'end', 'next', 'repeat', 'repeat_until']
    actions = [complete_pickup]


class EventAdmin(admin.ModelAdmin):
    list_display = ['info']


class PickUpResource(resources.ModelResource):
    class Meta:
        model = PickUpInfo


class PickUpInfoAdmin(ImportExportModelAdmin):
    list_display = ['id', 'user', 'bin_type', 'lbs', 'instructions']
    resource_class = PickUpResource


class CompletedPickUpResource(resources.ModelResource):
    class Meta:
        model = CompletedPickUp


class CompletedPickUpAdmin(ImportExportModelAdmin):
    list_display = ['id', 'user', 'pick_up_info', 'pick_up_date']
    resource_class = CompletedPickUpResource


class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'street_name', 'state', 'zip_code', 'city']


class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'notification_type', 'message', 'seen', 'created_date']


class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'reminder', 'notify']


admin.site.register(UserSettings, UserSettingsAdmin)
admin.site.register(UserNotification, UserNotificationAdmin)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(PickUpInfo, PickUpInfoAdmin)
admin.site.register(CompletedPickUp, CompletedPickUpAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
