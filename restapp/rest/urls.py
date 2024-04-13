from django.urls import path

from . import views

urlpatterns = [
    path("", views.nav_home),
    path("signin/", views.nav_signin),
    path("signup/", views.nav_signup),
    path("search/", views.nav_search),
    path("search/results", views.search_results),
    path("search/results/business", views.view_business)
]