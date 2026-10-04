from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from django import forms
from django.utils import timezone

from .models import Capsule
from .timezones import TZ_CHOICES, DEFAULT_TZ
from .translations import get_text as t

INPUT = (
    "w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-slate-100 "
    "placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-400/60 "
    "focus:border-transparent transition"
)
MAX_MESSAGE = 5000

# maydon -> (label kaliti, placeholder kaliti)
TEXT_KEYS = {
    'sender_name': ('sender_label', 'sender_ph'),
    'recipient_name': ('recipient_label', 'recipient_ph'),
    'message': ('message_label', 'message_ph'),
    'unlock_date': ('date_label', None),
    'unlock_time': ('time_label', None),
    'tz_name': ('tz_label', None),
}


class CapsuleForm(forms.ModelForm):
    # Butun dunyo vaqt mintaqalari
    tz_name = forms.ChoiceField(
        choices=TZ_CHOICES,
        initial=DEFAULT_TZ,
        widget=forms.Select(attrs={'class': INPUT}),
    )

    class Meta:
        model = Capsule
        fields = ['sender_name', 'recipient_name', 'message', 'unlock_date', 'unlock_time', 'tz_name']
        widgets = {
            'sender_name': forms.TextInput(attrs={'class': INPUT}),
            'recipient_name': forms.TextInput(attrs={'class': INPUT}),
            'message': forms.Textarea(attrs={'class': INPUT + " resize-none", 'rows': 8}),
            'unlock_date': forms.DateInput(format='%Y-%m-%d', attrs={'class': INPUT, 'type': 'date'}),
            'unlock_time': forms.TimeInput(format='%H:%M', attrs={'class': INPUT, 'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Joriy tilda: label, placeholder va xato xabarlari
        for name, field in self.fields.items():
            label_key, ph_key = TEXT_KEYS[name]
            field.label = t(label_key)
            if ph_key:
                field.widget.attrs['placeholder'] = t(ph_key)
            field.error_messages.update(
                required=t('err_required'),
                invalid=t('err_invalid'),
                max_length=t('err_max'),
                invalid_choice=t('err_tz'),
            )
        self.fields['unlock_date'].error_messages['invalid'] = t('err_date_invalid')
        self.fields['unlock_time'].error_messages['invalid'] = t('err_time_invalid')

        # Brauzer kalendarida o'tgan sanalarni o'chiramiz (aniq tekshiruv serverda)
        earliest = (timezone.now() - timedelta(hours=12)).date()
        self.fields['unlock_date'].widget.attrs['min'] = earliest.isoformat()
        self.fields['unlock_time'].initial = time(9, 0)

    def clean_sender_name(self):
        return self.cleaned_data['sender_name'].strip()

    def clean_recipient_name(self):
        return self.cleaned_data['recipient_name'].strip()

    def clean_message(self):
        message = self.cleaned_data['message'].strip()
        if not message:
            raise forms.ValidationError(t('err_required'))
        if len(message) > MAX_MESSAGE:
            raise forms.ValidationError(t('err_message_max').format(n=MAX_MESSAGE))
        return message

    def clean(self):
        """Tanlangan MINTAQA vaqti bo'yicha kelajakda bo'lishi shart."""
        data = super().clean()
        d, tm, tz = data.get('unlock_date'), data.get('unlock_time'), data.get('tz_name')
        if d and tm and tz:
            when = datetime.combine(d, tm, tzinfo=ZoneInfo(tz))
            if when <= timezone.now():
                self.add_error('unlock_date', t('err_past'))
        return data