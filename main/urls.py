from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.create_capsule, name='create_capsule'),
    path('lang/<str:code>/', views.set_language, name='set_language'),
    path('capsule/<uuid:pk>/success/', views.capsule_success, name='capsule_success'),
    path('capsule/<uuid:pk>/', views.view_capsule, name='view_capsule'),
]