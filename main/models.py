import uuid
from datetime import datetime, time
from zoneinfo import ZoneInfo

from django.db import models
from django.utils.formats import date_format


class Capsule(models.Model):
    """Kelajakka yozilgan xat (vaqt kapsulasi)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender_name = models.CharField("Yuboruvchi ismi", max_length=100)
    recipient_name = models.CharField("Qabul qiluvchi ismi", max_length=100)
    message = models.TextField("Xat matni")
    created_at = models.DateTimeField("Yaratilgan vaqt", auto_now_add=True)

    # --- Ochilish vaqti: sana + soat + vaqt mintaqasi ---
    unlock_date = models.DateField("Ochilish sanasi")
    unlock_time = models.TimeField("Ochilish soati", default=time(9, 0))
    tz_name = models.CharField("Vaqt mintaqasi", max_length=64, default='Asia/Tashkent')

    is_opened = models.BooleanField("Ochilganmi", default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Vaqt kapsulasi"
        verbose_name_plural = "Vaqt kapsulalari"

    def __str__(self):
        return f"{self.sender_name} → {self.recipient_name} ({self.unlock_date} {self.tz_name})"

    @property
    def unlock_datetime(self):
        """Ochilish momenti: tanlangan mintaqadagi sana+soat (timezone-aware)."""
        return datetime.combine(self.unlock_date, self.unlock_time, tzinfo=ZoneInfo(self.tz_name))

    @property
    def is_unlocked(self):
        from django.utils import timezone
        return timezone.now() >= self.unlock_datetime

    @property
    def unlock_text(self):
        """Odam o'qiydigan ko'rinish, joriy tilda."""
        return f"{date_format(self.unlock_date, 'j E Y')}, {self.unlock_time:%H:%M} ({self.tz_name})"