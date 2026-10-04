from django.conf import settings
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache

from .forms import CapsuleForm
from .models import Capsule


def set_language(request, code):
    """Tilni almashtirish: cookie'ga yozib, avvalgi sahifaga qaytaradi."""
    if code not in dict(settings.LANGUAGES):
        raise Http404
    next_url = request.META.get('HTTP_REFERER', '')
    if not url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        next_url = reverse('main:create_capsule')
    response = redirect(next_url)
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, code, max_age=60 * 60 * 24 * 365, samesite='Lax')
    return response


def create_capsule(request):
    if request.method == 'POST':
        form = CapsuleForm(request.POST)
        if form.is_valid():
            capsule = form.save()
            return redirect('main:capsule_success', pk=capsule.pk)
    else:
        form = CapsuleForm()
    return render(request, 'main/create_capsule.html', {'form': form})


def capsule_success(request, pk):
    capsule = get_object_or_404(Capsule, pk=pk)
    share_url = request.build_absolute_uri(reverse('main:view_capsule', args=[capsule.pk]))
    return render(request, 'main/capsule_success.html', {'capsule': capsule, 'share_url': share_url})


@never_cache
def view_capsule(request, pk):
    """MUHIM: qulflangan holatda xat matni shablonga UMUMAN uzatilmaydi."""
    capsule = get_object_or_404(Capsule, pk=pk)

    if capsule.is_unlocked:
        if not capsule.is_opened:
            capsule.is_opened = True
            capsule.save(update_fields=['is_opened'])
        return render(request, 'main/capsule_unlocked.html', {'capsule': capsule})

    return render(request, 'main/capsule_locked.html', {
        'sender_name': capsule.sender_name,
        'recipient_name': capsule.recipient_name,
        'when_text': capsule.unlock_text,
        'unlock_iso': capsule.unlock_datetime.isoformat(),
    })
# Create your views here.
