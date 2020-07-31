from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, PickUpInfo, Schedule


class CustomUserAdmin(UserAdmin):
    model = CustomUser

    fieldsets = UserAdmin.fieldsets + (
            (None, {'fields': ('type', 'phone_number',)}),
    )


class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['customer_id', 'event', 'first', 'next']


class PickUpInfoAdmin(admin.ModelAdmin):
    list_display = ['pk', 'bin_type', 'lbs', 'instructions']


admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(PickUpInfo, PickUpInfoAdmin)
admin.site.register(CustomUser, CustomUserAdmin)



