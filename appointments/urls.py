from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    # Template-based views
    path('', views.appointment_list, name='appointment-list'),
    path('doctor/', views.doctor_appointment_list, name='doctor-appointment-list'),
    path('<int:pk>/', views.appointment_detail, name='appointment-detail'),
    path('<int:pk>/cancel/', views.appointment_cancel, name='appointment-cancel'),
    path('create/<int:doctor_id>/', views.appointment_create, name='create'),

    # API views
    path('api/', views.AppointmentListView.as_view(), name='api-appointment-list'),
    path('api/<int:pk>/', views.AppointmentDetailView.as_view(), name='api-appointment-detail'),
    path('api/create/', views.AppointmentCreateView.as_view(), name='api-appointment-create'),
    path('api/<int:pk>/cancel/', views.AppointmentCancelView.as_view(), name='api-appointment-cancel'),
    path('api/my-appointments/', views.MyAppointmentsView.as_view(), name='api-my-appointments'),
] 