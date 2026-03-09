from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'human-doctors', views.HumanDoctorViewSet, basename='human-doctor')
router.register(r'vet-doctors', views.VetDoctorViewSet, basename='vet-doctor')

urlpatterns = [
    path('', include(router.urls)),
    path('translate-symptoms/', views.translate_symptoms, name='translate-symptoms'),
    path('analyze-symptoms/', views.analyze_symptoms, name='analyze-symptoms'),
    path('search-doctors/', views.search_doctors_by_symptoms, name='search-doctors'),
    
    # Appointment endpoints
    path('appointments/human/create/', views.create_human_appointment, name='create-human-appointment'),
    path('appointments/animal/create/', views.create_animal_appointment, name='create-animal-appointment'),
    path('appointments/<str:appointment_id>/', views.get_appointment_details, name='appointment-details'),
    path('appointments/<str:appointment_id>/status/', views.update_appointment_status, name='update-appointment-status'),
    
    # Doctor details
    path('doctors/<int:doctor_id>/', views.get_doctor_details, name='doctor-details'),
    path('doctors/<int:doctor_id>/slots/', views.get_available_slots, name='available-slots'),
    
    # Doctor authentication and dashboard
    path('doctor/login/', views.doctor_login, name='doctor-login'),
    path('doctor/register/', views.doctor_register, name='doctor-register'),
    path('doctor/appointments/', views.get_doctor_appointments, name='doctor-appointments'),
    path('doctor/profile/', views.get_doctor_profile, name='get-doctor-profile'),
    path('doctor/profile/update/', views.update_doctor_profile, name='update-doctor-profile'),
]
