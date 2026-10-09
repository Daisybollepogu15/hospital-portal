from django.urls import path
from . import views

urlpatterns = [
    # Home & Information
    path('', views.home, name='home'),
    path('departments/', views.departments_list, name='departments_list'),
    path('departments/<str:department_name>/', views.department_detail, name='department_detail'),

    # Doctor Directory
    path('doctors/', views.doctors_list, name='doctors_list'),
    path('doctors/<int:doctor_id>/', views.doctor_detail, name='doctor_detail'),

    # Appointment Booking & Flow
    path('book/', views.book_appointment, name='book_appointment'),
    path('book/<int:doctor_id>/', views.book_appointment, name='book_appointment_with_doctor'),
    path('appointment/<str:appointment_id>/confirmation/', views.appointment_confirmation, name='appointment_confirmation'),
    path('appointment/<str:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),

    # Patient Portal & Reports
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('report/<int:report_id>/', views.medical_report_detail, name='medical_report_detail'),

    # AJAX API for real-time slot availability
    path('api/booked-slots/', views.api_booked_slots, name='api_booked_slots'),
]
