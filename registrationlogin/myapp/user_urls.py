from django.urls import path
from myapp import views

urlpatterns = [
    path('register/', views.register_user),
    path('edit_profile/', views.edit_profile),
    path('login/',views.login_user),
    path('logout/',views.user_logout)
]