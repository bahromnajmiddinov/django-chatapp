from django.urls import path

from . import views


urlpatterns = [
    path('profile/', views.profile_redirect, name='my_profile'),
    path('profile/@<username>/', views.profile, name='profile'),
    path('profile/profile-edit/', views.profile_edit, name='profile-edit'),
]

