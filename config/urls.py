"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import home, dashboard, profile, admin_dashboard, CustomLoginView

urlpatterns = [
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('admin-dashboard/', admin_dashboard, name='admin-dashboard'),
    path('profile/', profile, name='profile'),
    path('admin/', admin.site.urls),
    path('api/doctors/', include('doctors.urls')),
    path('api/appointments/', include('appointments.urls', namespace='api_appointments')),
    path('appointments/', include('appointments.urls', namespace='appointments')),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/profile/', profile, name='profile'),
    path('accounts/', include('django.contrib.auth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
