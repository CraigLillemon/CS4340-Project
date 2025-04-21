from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.nav_home, name = 'home'),
    path("accounts/", include('django.contrib.auth.urls')),
    path('accounts/logout/', auth_views.LogoutView.as_view(template_name='registration/logged_out.html'), name='logout'),
    path('accounts/register/', views.register, name='register_page'),
    path("search/", views.nav_search),
    path("search/results", views.search_results),
    path("search/results/business", views.view_business),
    path("favorites/list", views.favorites_list, name='favorites_list'),
    path("favorites/restaurant/create_internal/", views.create_restaurant, name='create_restaurant_internal'),
    path("favorites/toggle/<int:restaurant_id>/", views.toggle_favorite),
    path("favorites/rate/<int:restaurant_id>/", views.rate_restaurant, name='rate_restaurant')
]