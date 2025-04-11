from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    # Template-based views
    path('schedule/', views.doctor_schedule, name='schedule'),

    # API views
    path('specializations/', views.SpecializationListView.as_view(), name='specialization-list'),
    path('', views.DoctorListView.as_view(), name='doctor-list'),
    path('<int:pk>/', views.DoctorDetailView.as_view(), name='doctor-detail'),
    path('<int:pk>/schedule/', views.DoctorScheduleView.as_view(), name='doctor-schedule'),
] 