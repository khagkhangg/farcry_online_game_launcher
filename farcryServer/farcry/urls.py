from django.conf.urls import url
from django.urls import include, path
from . import views

urlpatterns = [
    path(r'players/login/', views.login),
    path(r'players/logout/', views.logout),
    path(r'players/register/', views.register),
    path(r'players/update/', views.update),
    path(r'players/verify/', views.verify),
    path(r'players/check_availability/', views.check_availability),
    path(r'players/check_email/', views.check_email),
    path(r'players/check_player_name/', views.check_player_name),

    path(r'matches/submit/', views.submit),

    path(r'redirect/verification_success/', views.verification_success),
    path(r'redirect/verification_failure/', views.verification_failure),

]
