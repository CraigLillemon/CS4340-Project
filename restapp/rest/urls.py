from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import path, include
from . import views


urlpatterns = [
    path("", views.nav_home, name = 'home'),
    path("accounts/", include('django.contrib.auth.urls')),
    path('accounts/logout/', auth_views.LogoutView.as_view(template_name='registration/logged_out.html'), name='logout'),
    path('accounts/register/', views.register, name='register_page'),
    path("signup/", views.nav_signup),
    path("search/", views.nav_search),
    path("search/results", views.search_results),
    path("search/results/business", views.view_business)
]