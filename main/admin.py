from django.contrib import admin
from .models import Capsule


@admin.register(Capsule)
class CapsuleAdmin(admin.ModelAdmin):
    list_display = ('sender_name', 'recipient_name', 'unlock_date', 'unlock_time', 'tz_name', 'is_opened', 'created_at')
    readonly_fields = ('id', 'created_at')