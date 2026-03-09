from rest_framework.decorators import api_view

# ...existing code...

@api_view(['PATCH'])
def update_appointment_status(request, appointment_id):
    """
    Update the status of a human or animal appointment
    Body: { "status": "new_status", "type": "human"|"vet" }
    """
    status_value = request.data.get('status')
    appt_type = request.data.get('type', 'human')
    if not status_value:
        return Response({'error': 'Missing status'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        if appt_type == 'human':
            appt = HumanAppointment.objects.get(appointment_id=appointment_id)
        else:
            appt = AnimalAppointment.objects.get(appointment_id=appointment_id)
        appt.status = status_value
        appt.save()
        return Response({'success': True, 'appointment_id': appointment_id, 'status': appt.status})
    except (HumanAppointment.DoesNotExist, AnimalAppointment.DoesNotExist):
        return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.db.models import Q, Max
from django.db import models
from math import radians, cos, sin, asin, sqrt
from .models import HumanDoctor, VetDoctor, Patient, Animal, Address, HumanAppointment, AnimalAppointment, Owner, Gender
from .serializers import (
    HumanDoctorSerializer, VetDoctorSerializer,
    PatientSerializer, AnimalSerializer
)
from .ml.symptom_analyzer import SymptomAnalyzer
from .ml.enhanced_symptom_analyzer import EnhancedSymptomAnalyzer
from .ml.bedrock_translator import BedrockTranslator


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two points on Earth using Haversine formula
    Returns distance in kilometers
    """
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    km = 6371 * c
    return km


def get_coordinates_from_address(address_obj):
    """
    Extract or geocode coordinates from address
    For now, returns default coordinates - implement geocoding service later
    """
    # TODO: Implement geocoding service (Google Maps API, etc.)
    # Default to Mumbai coordinates for now
    return 19.0760, 72.8777


class HumanDoctorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for human doctor search and filtering
    """
    queryset = HumanDoctor.objects.select_related('address', 'gender').all()
    serializer_class = HumanDoctorSerializer
    
    def get_queryset(self):
        queryset = HumanDoctor.objects.select_related('address', 'gender').all()
        
        # Filter by specialization
        specialization = self.request.query_params.get('specialization', None)
        if specialization:
            queryset = queryset.filter(specialization__icontains=specialization)
        
        # Filter by city
        city = self.request.query_params.get('city', None)
        if city:
            queryset = queryset.filter(address__city__icontains=city)
        
        # Filter by status (active/inactive)
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """
        Find human doctors near a specific location
        Query params: latitude, longitude, radius (in km, default 10)
        """
        try:
            user_lat = float(request.query_params.get('latitude'))
            user_lon = float(request.query_params.get('longitude'))
            radius = float(request.query_params.get('radius', 10))
            specialization = request.query_params.get('specialization', None)
            
            queryset = HumanDoctor.objects.select_related('address', 'gender').all()
            
            if specialization:
                queryset = queryset.filter(specialization__icontains=specialization)
            
            doctors_with_distance = []
            for doctor in queryset:
                if doctor.address:
                    # Get coordinates from address
                    doc_lat, doc_lon = get_coordinates_from_address(doctor.address)
                    distance = haversine_distance(user_lat, user_lon, doc_lat, doc_lon)
                    
                    if distance <= radius:
                        doctor.distance = round(distance, 2)
                        doctors_with_distance.append(doctor)
            
            doctors_with_distance.sort(key=lambda x: x.distance)
            
            serializer = self.get_serializer(doctors_with_distance, many=True)
            return Response(serializer.data)
            
        except (TypeError, ValueError) as e:
            return Response(
                {'error': 'Invalid latitude, longitude, or radius parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )


class VetDoctorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for veterinary doctor search and filtering
    """
    queryset = VetDoctor.objects.all()
    serializer_class = VetDoctorSerializer
    
    def get_queryset(self):
        queryset = VetDoctor.objects.all()
        
        # Filter by specialty
        specialty = self.request.query_params.get('specialty', None)
        if specialty:
            queryset = queryset.filter(specialty__icontains=specialty)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """
        Find vet doctors near a specific location
        """
        try:
            user_lat = float(request.query_params.get('latitude'))
            user_lon = float(request.query_params.get('longitude'))
            radius = float(request.query_params.get('radius', 10))
            specialty = request.query_params.get('specialty', None)
            
            queryset = VetDoctor.objects.all()
            
            if specialty:
                queryset = queryset.filter(specialty__icontains=specialty)
            
            doctors_with_distance = []
            for doctor in queryset:
                # Parse address to get coordinates (implement geocoding)
                doc_lat, doc_lon = get_coordinates_from_address(None)
                distance = haversine_distance(user_lat, user_lon, doc_lat, doc_lon)
                
                if distance <= radius:
                    doctor.distance = round(distance, 2)
                    doctors_with_distance.append(doctor)
            
            doctors_with_distance.sort(key=lambda x: x.distance)
            
            serializer = self.get_serializer(doctors_with_distance, many=True)
            return Response(serializer.data)
            
        except (TypeError, ValueError) as e:
            return Response(
                {'error': 'Invalid parameters'},
                status=status.HTTP_400_BAD_REQUEST
            )


@api_view(['POST'])
def translate_symptoms(request):
    """
    Translate Marathi/Hindi symptoms to English using AWS Bedrock
    Body: { "text": "...", "source_language": "auto|marathi|hindi" }
    """
    text = request.data.get('text', '')
    source_language = request.data.get('source_language', 'auto')
    
    if not text:
        return Response(
            {'error': 'Text is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        translator = BedrockTranslator()
        result = translator.translate_to_english(text, source_language)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': result.get('error', 'Translation failed')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    except Exception as e:
        return Response(
            {'error': f'Translation service error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def analyze_symptoms(request):
    """
    Analyze symptoms and return recommended specialties
    Body: { "symptoms": "...", "patient_type": "human" or "pet" }
    """
    symptoms = request.data.get('symptoms', '')
    patient_type = request.data.get('patient_type', 'human')
    
    if not symptoms:
        return Response(
            {'error': 'Symptoms are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Use enhanced analyzer with comprehensive training data
    analyzer = EnhancedSymptomAnalyzer()
    result = analyzer.analyze_symptoms(symptoms, patient_type)
    severity = analyzer.extract_severity(symptoms)
    
    result['severity'] = severity
    
    return Response(result, status=status.HTTP_200_OK)


@api_view(['POST'])
def search_doctors_by_symptoms(request):
    """
    Advanced endpoint: analyze symptoms and find matching doctors nearby with AI ranking
    Body: {
        "symptoms": "...",
        "patient_type": "human" or "pet",
        "latitude": float,
        "longitude": float,
        "radius": float (optional, default 10km)
    }
    """
    symptoms = request.data.get('symptoms', '')
    patient_type = request.data.get('patient_type', 'human')
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    radius = request.data.get('radius', 10)

    if not symptoms:
        return Response({'error': 'Symptoms are required'}, status=status.HTTP_400_BAD_REQUEST)

    # Initialize analyzer
    analyzer = SymptomAnalyzer()

    # Analyze symptoms
    analysis = analyzer.analyze_symptoms(symptoms, patient_type)

    # Find matching doctors
    doctors_list = []

    if latitude and longitude:
        if patient_type == 'human':
            queryset = HumanDoctor.objects.select_related('address', 'gender').all()

            # Filter by recommended specialties
            if analysis['recommended_specialties']:
                specialty_query = Q()
                for specialty in analysis['recommended_specialties']:
                    specialty_query |= Q(specialization__icontains=specialty)
                queryset = queryset.filter(specialty_query)

            # Calculate distances and prepare doctor data
            for doctor in queryset:
                if doctor.address:
                    doc_lat, doc_lon = get_coordinates_from_address(doctor.address)
                    distance = haversine_distance(
                        float(latitude), float(longitude),
                        doc_lat, doc_lon
                    )

                    if distance <= float(radius):
                        doctor_dict = {
                            'doctor_id': doctor.doctor_id,
                            'first_name': doctor.first_name,
                            'last_name': doctor.last_name,
                            'specialization': doctor.specialization,
                            'yoe': doctor.yoe,
                            'contact_number': doctor.contact_number,
                            'rating': 4.5,  # Default rating
                            'distance': round(distance, 2),
                            'address_details': {
                                'city': doctor.address.city,
                                'state': doctor.address.state,
                                'address': doctor.address.address
                            } if doctor.address else None,
                            'gender_name': doctor.gender.name if doctor.gender else None,
                            'status': doctor.status,
                            'open_time_1': str(doctor.open_time_1) if doctor.open_time_1 else None,
                            'close_time_1': str(doctor.close_time_1) if doctor.close_time_1 else None,
                        }
                        doctors_list.append(doctor_dict)

        else:  # pet
            queryset = VetDoctor.objects.all()

            # Filter by recommended specialties
            if analysis['recommended_specialties']:
                specialty_query = Q()
                for specialty in analysis['recommended_specialties']:
                    specialty_query |= Q(specialty__icontains=specialty)
                queryset = queryset.filter(specialty_query)

            # Calculate distances
            for doctor in queryset:
                doc_lat, doc_lon = get_coordinates_from_address(None)
                distance = haversine_distance(
                    float(latitude), float(longitude),
                    doc_lat, doc_lon
                )

                if distance <= float(radius):
                    doctor_dict = {
                        'doctor_id': doctor.doctor_id,
                        'name': doctor.name,
                        'specialty': doctor.specialty,
                        'specialization': doctor.specialty,
                        'clinic_name': doctor.clinic_name,
                        'experience': doctor.experience,
                        'rating': 4.5,  # Default rating
                        'distance': round(distance, 2),
                        'address': doctor.address,
                        'gender': doctor.gender,
                        'license_number': doctor.license_number,
                    }
                    doctors_list.append(doctor_dict)

        # Use AI to rank doctors based on symptom match
        ranked_doctors = analyzer.match_doctors_to_symptoms(
            symptoms,
            patient_type,
            doctors_list
        )

        return Response({
            'analysis': analysis,
            'doctors': ranked_doctors,
            'total_found': len(ranked_doctors),
            'search_radius': radius
        }, status=status.HTTP_200_OK)

    return Response({
        'analysis': analysis,
        'doctors': [],
        'message': 'Location required for doctor search'
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
def search_doctors_by_symptoms(request):
    """
    Advanced endpoint with progressive radius expansion and city-based fallback
    Uses Enhanced Symptom Analyzer with comprehensive training data
    """
    symptoms = request.data.get('symptoms', '')
    patient_type = request.data.get('patient_type', 'human')
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    initial_radius = request.data.get('radius', 10)
    
    if not symptoms:
        return Response({'error': 'Symptoms are required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Use enhanced analyzer with comprehensive training data
    analyzer = EnhancedSymptomAnalyzer()
    analysis = analyzer.analyze_symptoms(symptoms, patient_type)
    
    doctors_list = []
    search_attempts = []
    radius = initial_radius
    max_radius = 100
    
    if latitude and longitude:
        # Progressive radius expansion
        while len(doctors_list) == 0 and radius <= max_radius:
            search_attempts.append({'radius': radius, 'method': 'location_based'})
            
            if patient_type == 'human':
                queryset = HumanDoctor.objects.select_related('address', 'gender').all()
                
                if analysis['recommended_specialties']:
                    specialty_query = Q()
                    for specialty in analysis['recommended_specialties']:
                        specialty_query |= Q(specialization__icontains=specialty)
                    queryset = queryset.filter(specialty_query)
                
                for doctor in queryset:
                    if doctor.address:
                        doc_lat, doc_lon = get_coordinates_from_address(doctor.address)
                        distance = haversine_distance(float(latitude), float(longitude), doc_lat, doc_lon)
                        
                        if distance <= float(radius):
                            doctor_dict = {
                                'doctor_id': doctor.doctor_id,
                                'first_name': doctor.first_name,
                                'last_name': doctor.last_name,
                                'specialization': doctor.specialization,
                                'years_experience': doctor.years_experience,
                                'phone_number': doctor.phone_number,
                                'rating': 4.5,
                                'distance': round(distance, 2),
                                'address_details': {
                                    'city': doctor.address.city,
                                    'state': doctor.address.state,
                                    'address': doctor.address.address
                                } if doctor.address else None,
                                'gender_name': doctor.gender.name if doctor.gender else None,
                                'status': doctor.status,
                                'open_time_1': str(doctor.open_time_1) if doctor.open_time_1 else None,
                                'close_time_1': str(doctor.close_time_1) if doctor.close_time_1 else None,
                            }
                            doctors_list.append(doctor_dict)
            
            else:  # pet
                queryset = VetDoctor.objects.all()
                
                if analysis['recommended_specialties']:
                    specialty_query = Q()
                    for specialty in analysis['recommended_specialties']:
                        specialty_query |= Q(specialty__icontains=specialty)
                    queryset = queryset.filter(specialty_query)
                
                for doctor in queryset:
                    doc_lat, doc_lon = get_coordinates_from_address(None)
                    distance = haversine_distance(float(latitude), float(longitude), doc_lat, doc_lon)
                    
                    if distance <= float(radius):
                        doctor_dict = {
                            'doctor_id': doctor.doctor_id,
                            'name': doctor.name,
                            'specialty': doctor.specialty,
                            'specialization': doctor.specialty,
                            'clinic_name': doctor.clinic_name,
                            'experience': doctor.experience,
                            'rating': 4.5,
                            'distance': round(distance, 2),
                            'address': doctor.address,
                            'gender': doctor.gender,
                            'license_number': doctor.license_number,
                        }
                        doctors_list.append(doctor_dict)
            
            # Expand radius if no doctors found
            if len(doctors_list) == 0:
                if radius < 20:
                    radius = 20
                elif radius < 50:
                    radius = 50
                elif radius < 100:
                    radius = 100
                else:
                    break
        
        # City-based fallback search
        if len(doctors_list) == 0:
            search_attempts.append({'method': 'city_based', 'message': 'Searching by nearest cities'})
            
            if patient_type == 'human':
                queryset = HumanDoctor.objects.select_related('address', 'gender').all()
                
                if analysis['recommended_specialties']:
                    specialty_query = Q()
                    for specialty in analysis['recommended_specialties']:
                        specialty_query |= Q(specialization__icontains=specialty)
                    queryset = queryset.filter(specialty_query)
                
                # Find nearest cities
                city_distances = {}
                for doctor in queryset:
                    if doctor.address and doctor.address.city:
                        doc_lat, doc_lon = get_coordinates_from_address(doctor.address)
                        distance = haversine_distance(float(latitude), float(longitude), doc_lat, doc_lon)
                        city = doctor.address.city
                        if city not in city_distances or distance < city_distances[city]:
                            city_distances[city] = distance
                
                # Get top 3 nearest cities
                nearest_cities = sorted(city_distances.items(), key=lambda x: x[1])[:3]
                
                # Search doctors in nearest cities
                for city, city_distance in nearest_cities:
                    city_doctors = queryset.filter(address__city__iexact=city)
                    
                    for doctor in city_doctors:
                        if doctor.address:
                            doc_lat, doc_lon = get_coordinates_from_address(doctor.address)
                            distance = haversine_distance(float(latitude), float(longitude), doc_lat, doc_lon)
                            
                            doctor_dict = {
                                'doctor_id': doctor.doctor_id,
                                'first_name': doctor.first_name,
                                'last_name': doctor.last_name,
                                'specialization': doctor.specialization,
                                'yoe': doctor.yoe,
                                'contact_number': doctor.contact_number,
                                'rating': 4.5,
                                'distance': round(distance, 2),
                                'address_details': {
                                    'city': doctor.address.city,
                                    'state': doctor.address.state,
                                    'address': doctor.address.address
                                } if doctor.address else None,
                                'gender_name': doctor.gender.name if doctor.gender else None,
                                'status': doctor.status,
                                'open_time_1': str(doctor.open_time_1) if doctor.open_time_1 else None,
                                'close_time_1': str(doctor.close_time_1) if doctor.close_time_1 else None,
                                'nearest_city': city
                            }
                            doctors_list.append(doctor_dict)
                    
                    if len(doctors_list) >= 20:
                        break
            
            else:  # pet
                queryset = VetDoctor.objects.all()
                
                if analysis['recommended_specialties']:
                    specialty_query = Q()
                    for specialty in analysis['recommended_specialties']:
                        specialty_query |= Q(specialty__icontains=specialty)
                    queryset = queryset.filter(specialty_query)
                
                for doctor in queryset[:20]:
                    doc_lat, doc_lon = get_coordinates_from_address(None)
                    distance = haversine_distance(float(latitude), float(longitude), doc_lat, doc_lon)
                    
                    doctor_dict = {
                        'doctor_id': doctor.doctor_id,
                        'name': doctor.name,
                        'specialty': doctor.specialty,
                        'specialization': doctor.specialty,
                        'clinic_name': doctor.clinic_name,
                        'experience': doctor.experience,
                        'rating': 4.5,
                        'distance': round(distance, 2),
                        'address': doctor.address,
                        'gender': doctor.gender,
                        'license_number': doctor.license_number,
                    }
                    doctors_list.append(doctor_dict)
        
        # AI ranking
        ranked_doctors = analyzer.match_doctors_to_symptoms(symptoms, patient_type, doctors_list)
        
        return Response({
            'analysis': analysis,
            'doctors': ranked_doctors,
            'total_found': len(ranked_doctors),
            'search_radius': radius,
            'initial_radius': initial_radius,
            'search_attempts': search_attempts,
            'search_expanded': radius > initial_radius,
            'city_based_search': len(search_attempts) > 0 and search_attempts[-1].get('method') == 'city_based'
        }, status=status.HTTP_200_OK)
    
    return Response({
        'analysis': analysis,
        'doctors': [],
        'message': 'Location required for doctor search'
    }, status=status.HTTP_200_OK)



@api_view(['POST'])
def create_human_appointment(request):
    """
    Create a new appointment for human patient with slot validation
    """
    from .serializers import CreateHumanAppointmentSerializer, AppointmentDetailSerializer
    from datetime import datetime
    
    serializer = CreateHumanAppointmentSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {'error': 'Invalid data', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    data = serializer.validated_data
    
    try:
        # Check if doctor exists
        doctor = HumanDoctor.objects.get(doctor_id=data['doctor_id'])
        
        # Validate slot availability
        existing_appointment = HumanAppointment.objects.filter(
            doctor=doctor,
            scheduling_date=data['scheduling_date'],
            scheduling_time=data['scheduling_time'],
            status__in=['scheduled', 'confirmed']
        ).first()
        
        if existing_appointment:
            return Response(
                {
                    'error': 'Slot not available',
                    'message': f'This time slot is already booked. Please select another time.',
                    'booked_slot': {
                        'date': str(data['scheduling_date']),
                        'time': str(data['scheduling_time'])
                    }
                },
                status=status.HTTP_409_CONFLICT
            )
        
        # Create or get patient
        patient, created = Patient.objects.get_or_create(
            first_name=data['patient_first_name'],
            last_name=data['patient_last_name'],
            contact_number=data['contact_number'],
            defaults={
                'email_id': data.get('email_id', ''),
                'date_of_birth': data.get('date_of_birth'),
                'gender_id': data.get('gender_id'),
                'registration_date': datetime.now().date()
            }
        )
        
        # Create appointment
        appointment = HumanAppointment.objects.create(
            patient=patient,
            doctor=doctor,
            scheduling_date=data['scheduling_date'],
            scheduling_time=data['scheduling_time'],
            status='scheduled',
            age=data.get('age')
        )
        
        # Serialize response
        response_serializer = AppointmentDetailSerializer(appointment)
        
        return Response({
            'success': True,
            'message': 'Appointment booked successfully',
            'appointment': response_serializer.data,
            'appointment_id': appointment.appointment_id,
            'patient_created': created,
            'booking_details': {
                'doctor_name': f"Dr. {doctor.first_name} {doctor.last_name}",
                'patient_name': f"{patient.first_name} {patient.last_name}",
                'date': str(data['scheduling_date']),
                'time': str(data['scheduling_time'])
            }
        }, status=status.HTTP_201_CREATED)
        
    except HumanDoctor.DoesNotExist:
        return Response(
            {'error': 'Doctor not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': 'Failed to create appointment', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def create_animal_appointment(request):
    """
    Create a new appointment for animal patient with slot validation
    """
    from .serializers import CreateAnimalAppointmentSerializer
    from .models import Owner
    from datetime import datetime, time
    
    serializer = CreateAnimalAppointmentSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {'error': 'Invalid data', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    data = serializer.validated_data
    
    try:
        # Check if vet doctor exists
        doctor = VetDoctor.objects.get(doctor_id=data['doctor_id'])
        
        # For animal appointments, we need to add time field to the model
        # For now, we'll check if there's already an appointment on the same date
        existing_appointment = AnimalAppointment.objects.filter(
            doctor=doctor,
            appointment_date=data['appointment_date'],
            status__in=['scheduled', 'confirmed']
        ).first()
        
        if existing_appointment:
            return Response(
                {
                    'error': 'Slot not available',
                    'message': f'This date already has an appointment booked. Please select another date.',
                    'booked_date': str(data['appointment_date'])
                },
                status=status.HTTP_409_CONFLICT
            )
        
        # Create or get owner
        owner, owner_created = Owner.objects.get_or_create(
            owner_name=data['owner_name'],
            phone=data['owner_phone'],
            defaults={
                'email': data.get('owner_email', '')
            }
        )
        
        # Create or get animal
        animal, animal_created = Animal.objects.get_or_create(
            animal_name=data['animal_name'],
            owner=owner,
            defaults={
                'species': data.get('species', ''),
                'breed': data.get('breed', ''),
                'age': data.get('age'),
                'gender': data.get('gender', ''),
                'weight': data.get('weight')
            }
        )
        
        # Create appointment
        appointment = AnimalAppointment.objects.create(
            doctor=doctor,
            animal=animal,
            appointment_date=data['appointment_date'],
            status='scheduled'
        )
        
        return Response({
            'success': True,
            'message': 'Appointment booked successfully',
            'appointment_id': appointment.appointment_id,
            'owner_created': owner_created,
            'animal_created': animal_created,
            'booking_details': {
                'doctor_name': doctor.name,
                'animal_name': animal.animal_name,
                'owner_name': owner.owner_name,
                'date': str(data['appointment_date']),
                'clinic': doctor.clinic_name or 'N/A'
            },
            'appointment': {
                'appointment_id': appointment.appointment_id,
                'appointment_date': appointment.appointment_date,
                'status': appointment.status,
                'doctor_name': doctor.name,
                'animal_name': animal.animal_name,
                'owner_name': owner.owner_name
            }
        }, status=status.HTTP_201_CREATED)
        
    except VetDoctor.DoesNotExist:
        return Response(
            {'error': 'Veterinary doctor not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': 'Failed to create appointment', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_doctor_details(request, doctor_id):
    """
    Get detailed information about a doctor
    """
    patient_type = request.query_params.get('type', 'human')
    
    try:
        if patient_type == 'human':
            doctor = HumanDoctor.objects.select_related('address', 'gender').get(doctor_id=doctor_id)
            serializer = HumanDoctorSerializer(doctor)
            return Response({
                'success': True,
                'doctor': serializer.data,
                'type': 'human'
            })
        else:
            doctor = VetDoctor.objects.get(doctor_id=doctor_id)
            serializer = VetDoctorSerializer(doctor)
            return Response({
                'success': True,
                'doctor': serializer.data,
                'type': 'pet'
            })
    except (HumanDoctor.DoesNotExist, VetDoctor.DoesNotExist):
        return Response(
            {'error': 'Doctor not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def get_appointment_details(request, appointment_id):
    """
    Get appointment details by ID
    """
    patient_type = request.query_params.get('type', 'human')
    
    try:
        if patient_type == 'human':
            appointment = HumanAppointment.objects.select_related(
                'patient', 'doctor', 'doctor__address', 'doctor__gender'
            ).get(appointment_id=appointment_id)
            
            serializer = AppointmentDetailSerializer(appointment)
            return Response({
                'success': True,
                'appointment': serializer.data
            })
        else:
            appointment = AnimalAppointment.objects.select_related(
                'animal', 'doctor'
            ).get(appointment_id=appointment_id)
            
            serializer = AnimalAppointmentSerializer(appointment)
            return Response({
                'success': True,
                'appointment': serializer.data
            })
    except (HumanAppointment.DoesNotExist, AnimalAppointment.DoesNotExist):
        return Response(
            {'error': 'Appointment not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def get_available_slots(request, doctor_id):
    """
    Get available appointment slots for a doctor on a specific date
    """
    from datetime import datetime, timedelta
    
    date_str = request.query_params.get('date')
    patient_type = request.query_params.get('type', 'human')
    
    if not date_str:
        return Response(
            {'error': 'Date parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        if patient_type == 'human':
            doctor = HumanDoctor.objects.get(doctor_id=doctor_id)
            
            # Get doctor's working hours
            if doctor.open_time_1 and doctor.close_time_1:
                start_time = doctor.open_time_1
                end_time = doctor.close_time_1
            else:
                # Default hours
                start_time = datetime.strptime('09:00', '%H:%M').time()
                end_time = datetime.strptime('17:00', '%H:%M').time()
            
            # Get existing appointments for this date
            booked_times = HumanAppointment.objects.filter(
                doctor=doctor,
                scheduling_date=appointment_date,
                status__in=['scheduled', 'confirmed']
            ).values_list('scheduling_time', flat=True)
            
        else:
            doctor = VetDoctor.objects.get(doctor_id=doctor_id)
            
            if doctor.open_time_1 and doctor.close_time_1:
                start_time = doctor.open_time_1
                end_time = doctor.close_time_1
            else:
                start_time = datetime.strptime('09:00', '%H:%M').time()
                end_time = datetime.strptime('17:00', '%H:%M').time()
            
            has_appointment = AnimalAppointment.objects.filter(
                doctor=doctor,
                appointment_date=appointment_date,
                status__in=['scheduled', 'confirmed']
            ).exists()  # Check if any appointment exists on this date
        
        # Generate time slots (30-minute intervals)
        slots = []
        current_time = datetime.combine(appointment_date, start_time)
        end_datetime = datetime.combine(appointment_date, end_time)
        
        while current_time < end_datetime:
            slot_time = current_time.time()
            if patient_type == 'human':
                is_available = slot_time not in booked_times
            else:
                is_available = not has_appointment
            
            slots.append({
                'time': slot_time.strftime('%H:%M'),
                'display': current_time.strftime('%I:%M %p'),
                'available': is_available
            })
            
            current_time += timedelta(minutes=30)
        
        return Response({
            'success': True,
            'date': date_str,
            'doctor_id': doctor_id,
            'slots': slots
        })
        
    except (HumanDoctor.DoesNotExist, VetDoctor.DoesNotExist):
        return Response(
            {'error': 'Doctor not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except ValueError:
        return Response(
            {'error': 'Invalid date format. Use YYYY-MM-DD'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
def create_human_appointment(request):
    """
    Create a new human appointment
    """
    from .serializers import CreateHumanAppointmentSerializer
    
    serializer = CreateHumanAppointmentSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    try:
        # Get or create patient
        patient = Patient.objects.filter(
            first_name=data['patient_first_name'],
            last_name=data['patient_last_name'],
            contact_number=data['contact_number']
        ).first()
        
        if not patient:
            # Generate patient_id
            max_id = Patient.objects.aggregate(max_id=models.Max('patient_id'))['max_id']
            if max_id:
                # Extract number from 'PO52' format
                try:
                    num = int(max_id[2:]) + 1
                except (ValueError, IndexError):
                    num = 1
            else:
                num = 1
            patient_id = f'PO{num:02d}'
            
            patient_defaults = {
                'patient_id': patient_id,
                'email_id': data.get('email_id', ''),
                'date_of_birth': data.get('date_of_birth')
            }
            
            if data.get('gender_id'):
                try:
                    gender = Gender.objects.get(gender_id=str(data['gender_id']))
                    patient_defaults['gender'] = gender
                except Gender.DoesNotExist:
                    pass  # Skip if gender not found
            
            patient = Patient(**patient_defaults)
            patient.first_name = data['patient_first_name']
            patient.last_name = data['patient_last_name']
            patient.contact_number = data['contact_number']
            patient.save()
        
        # Get doctor
        doctor = HumanDoctor.objects.get(doctor_id=data['doctor_id'])
        
        # Check if slot is available
        existing_appointment = HumanAppointment.objects.filter(
            doctor=doctor,
            scheduling_date=data['scheduling_date'],
            scheduling_time=data['scheduling_time'],
            status__in=['scheduled', 'confirmed']
        ).exists()
        
        if existing_appointment:
            return Response(
                {'error': 'This time slot is already booked'},
                status=status.HTTP_409_CONFLICT
            )
        
        # Create appointment
        # Generate appointment_id
        max_id = HumanAppointment.objects.aggregate(max_id=Max('appointment_id'))['max_id']
        if max_id:
            # Extract number from 'AP00146' format
            try:
                num = int(max_id[2:]) + 1
            except (ValueError, IndexError):
                num = 1
        else:
            num = 1
        appointment_id = f'AP{num:05d}'
        
        appointment = HumanAppointment.objects.create(
            appointment_id=appointment_id,
            patient=patient,
            doctor=doctor,
            scheduling_date=data['scheduling_date'],
            scheduling_time=data['scheduling_time'],
            status='scheduled',
            age=data.get('age')
        )
        
        return Response({
            'success': True,
            'appointment_id': appointment.appointment_id,
            'message': 'Appointment booked successfully'
        }, status=status.HTTP_201_CREATED)
        
    except HumanDoctor.DoesNotExist:
        return Response(
            {'error': 'Doctor not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to create appointment: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def create_animal_appointment(request):
    """
    Create a new animal appointment
    """
    from .serializers import CreateAnimalAppointmentSerializer
    
    serializer = CreateAnimalAppointmentSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    try:
        # Get or create owner
        owner = Owner.objects.filter(
            owner_name=data['owner_name'],
            phone=data['owner_phone']
        ).first()
        
        if not owner:
            # Generate owner_id
            max_id = Owner.objects.aggregate(max_id=Max('owner_id'))['max_id']
            if max_id:
                # Extract number from 'O001' format
                try:
                    num = int(max_id[1:]) + 1
                except (ValueError, IndexError):
                    num = 1
            else:
                num = 1
            owner_id = f'O{num:03d}'
            
            owner = Owner.objects.create(
                owner_id=owner_id,
                owner_name=data['owner_name'],
                phone=data['owner_phone'],
                email=data.get('owner_email', '')
            )
        
        # Get or create animal
        animal = Animal.objects.filter(
            animal_name=data['animal_name'],
            owner=owner
        ).first()
        
        if not animal:
            # Generate animal_id
            max_id = Animal.objects.aggregate(max_id=Max('animal_id'))['max_id']
            if max_id:
                # Extract number from 'A001' format
                try:
                    num = int(max_id[1:]) + 1
                except (ValueError, IndexError):
                    num = 1
            else:
                num = 1
            animal_id = f'A{num:03d}'
            
            animal = Animal.objects.create(
                animal_id=animal_id,
                animal_name=data['animal_name'],
                owner=owner,
                species=data['species'],
                breed=data.get('breed', ''),
                age=data.get('age'),
                gender=data.get('gender', ''),
                weight=data.get('weight')
            )
        
        # Get doctor
        doctor = VetDoctor.objects.get(doctor_id=data['doctor_id'])
        
        # Check if there's already an appointment on this date for this doctor
        existing_appointment = AnimalAppointment.objects.filter(
            doctor=doctor,
            appointment_date=data['appointment_date'],
            status__in=['scheduled', 'confirmed']
        ).exists()
        
        if existing_appointment:
            return Response(
                {'error': 'This doctor already has an appointment on this date'},
                status=status.HTTP_409_CONFLICT
            )
        
        # Create appointment
        # Generate appointment_id
        max_id = AnimalAppointment.objects.aggregate(max_id=Max('appointment_id'))['max_id']
        if max_id:
            # Extract number from 'AP001' format
            try:
                num = int(max_id[2:]) + 1
            except (ValueError, IndexError):
                num = 1
        else:
            num = 1
        appointment_id = f'AP{num:03d}'
        
        appointment = AnimalAppointment.objects.create(
            appointment_id=appointment_id,
            doctor=doctor,
            animal=animal,
            appointment_date=data['appointment_date'],
            status='scheduled'
        )
        
        return Response({
            'success': True,
            'appointment_id': appointment.appointment_id,
            'message': 'Appointment booked successfully'
        }, status=status.HTTP_201_CREATED)
        
    except VetDoctor.DoesNotExist:
        return Response(
            {'error': 'Doctor not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to create appointment: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_appointment_details(request, appointment_id):
    """
    Get details of a specific appointment
    """
    from .serializers import AppointmentDetailSerializer
    
    try:
        # Try human appointment first
        try:
            appointment = HumanAppointment.objects.select_related(
                'patient', 'doctor', 'doctor__address', 'doctor__gender'
            ).get(appointment_id=appointment_id)
            
            serializer = AppointmentDetailSerializer(appointment)
            data = serializer.data
            data['appointment_type'] = 'human'
            return Response(data)
            
        except HumanAppointment.DoesNotExist:
            # Try animal appointment
            appointment = AnimalAppointment.objects.select_related(
                'animal', 'animal__owner', 'doctor'
            ).get(appointment_id=appointment_id)
            
            # For animal appointments, we need to create a custom response
            data = {
                'appointment_id': appointment.appointment_id,
                'appointment_date': appointment.appointment_date,
                'status': appointment.status,
                'appointment_type': 'animal',
                'animal_details': {
                    'animal_id': appointment.animal.animal_id,
                    'animal_name': appointment.animal.animal_name,
                    'species': appointment.animal.species,
                    'breed': appointment.animal.breed,
                    'age': appointment.animal.age,
                    'gender': appointment.animal.gender,
                    'weight': appointment.animal.weight,
                    'owner': {
                        'owner_id': appointment.animal.owner.owner_id,
                        'owner_name': appointment.animal.owner.owner_name,
                        'phone': appointment.animal.owner.phone,
                        'email': appointment.animal.owner.email
                    }
                },
                'doctor_details': {
                    'doctor_id': appointment.doctor.doctor_id,
                    'name': appointment.doctor.name,
                    'specialty': appointment.doctor.specialty,
                    'clinic_name': appointment.doctor.clinic_name,
                    'experience': appointment.doctor.experience,
                    'license_number': appointment.doctor.license_number,
                    'phone': appointment.doctor.phone,
                    'address': appointment.doctor.address
                }
            }
            return Response(data)
            
    except AnimalAppointment.DoesNotExist:
        return Response(
            {'error': 'Appointment not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to retrieve appointment: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )




# Doctor Authentication and Dashboard Views

@api_view(['POST'])
def doctor_login(request):
    """
    Doctor login endpoint
    Body: { "email": "...", "password": "...", "doctorType": "human" or "vet" }
    """
    import hashlib
    
    email = request.data.get('email', '').strip().lower()
    password = request.data.get('password', '')
    doctor_type = request.data.get('doctorType', 'human')
    
    if not email or not password:
        return Response(
            {'error': 'Email and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Hash password for comparison
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        from django.db import connection
        
        if doctor_type == 'human':
            with connection.cursor() as cursor:
                # First check if email exists
                cursor.execute(
                    "SELECT doctor_id, first_name, last_name, email, password_hash FROM human_doctors WHERE email = %s",
                    [email]
                )
                row = cursor.fetchone()
                
                if not row:
                    # User doesn't exist
                    return Response({
                        'error': 'User does not exist. Please register first.',
                        'errorType': 'USER_NOT_FOUND',
                        'redirectTo': 'register'
                    }, status=status.HTTP_404_NOT_FOUND)
                
                doctor_id, first_name, last_name, stored_email, stored_password_hash = row
                
                # Check if password matches
                if stored_password_hash != password_hash:
                    return Response({
                        'error': 'Login password is not matching. Please try again.',
                        'errorType': 'INVALID_PASSWORD'
                    }, status=status.HTTP_401_UNAUTHORIZED)
                
                # Successful login
                token = hashlib.sha256(f"{doctor_id}{email}".encode()).hexdigest()
                
                return Response({
                    'success': True,
                    'token': token,
                    'doctor_id': doctor_id,
                    'doctor_name': f"Dr. {first_name} {last_name}",
                    'doctor_type': 'human'
                })
                
        else:  # vet
            with connection.cursor() as cursor:
                # First check if email exists
                cursor.execute(
                    "SELECT doctor_id, name, email, password_hash FROM animal_doctors WHERE email = %s",
                    [email]
                )
                row = cursor.fetchone()
                
                if not row:
                    # User doesn't exist
                    return Response({
                        'error': 'User does not exist. Please register first.',
                        'errorType': 'USER_NOT_FOUND',
                        'redirectTo': 'register'
                    }, status=status.HTTP_404_NOT_FOUND)
                
                doctor_id, name, stored_email, stored_password_hash = row
                
                # Check if password matches
                if stored_password_hash != password_hash:
                    return Response({
                        'error': 'Login password is not matching. Please try again.',
                        'errorType': 'INVALID_PASSWORD'
                    }, status=status.HTTP_401_UNAUTHORIZED)
                
                # Successful login
                token = hashlib.sha256(f"{doctor_id}{email}".encode()).hexdigest()
                
                return Response({
                    'success': True,
                    'token': token,
                    'doctor_id': doctor_id,
                    'doctor_name': name,
                    'doctor_type': 'vet'
                })
        
    except Exception as e:
        import traceback
        print(f"Login error: {traceback.format_exc()}")
        return Response(
            {'error': f'Login failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def doctor_register(request):
    """
    Doctor registration endpoint
    """
    import hashlib
    from django.db import connection, transaction
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        data = request.data
        logger.info(f"Registration request received: {data}")
        
        doctor_type = data.get('doctorType', 'human')
        
        # Validate required fields
        required_fields = ['firstName', 'lastName', 'email', 'password', 'phoneNumber', 
                          'gender', 'age', 'specialization', 'yearsExperience', 
                          'registrationNumber', 'passoutDate']
        
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            logger.error(f"Missing fields: {missing_fields}")
            return Response(
                {'error': f'Missing required fields: {", ".join(missing_fields)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Hash password
        password_hash = hashlib.sha256(data['password'].encode()).hexdigest()
        
        with transaction.atomic():
            with connection.cursor() as cursor:
                if doctor_type == 'human':
                    # Check if email already exists
                    cursor.execute("SELECT doctor_id FROM human_doctors WHERE email = %s", [data['email']])
                    if cursor.fetchone():
                        return Response(
                            {'error': 'Email already registered'},
                            status=status.HTTP_409_CONFLICT
                        )
                    
                    # Get or create gender
                    gender_id = None
                    if data.get('gender'):
                        gender_map = {'Male': 'M', 'Female': 'F', 'Other': 'O'}
                        gender_id = gender_map.get(data['gender'], 'O')
                    
                    # Create address if provided
                    address_id = None
                    if data.get('address') or data.get('city') or data.get('state'):
                        # Generate address_id
                        cursor.execute("SELECT COALESCE(MAX(CAST(SUBSTRING(address_id FROM 5) AS INTEGER)), 0) FROM address WHERE address_id ~ '^ADDR[0-9]+'")
                        result = cursor.fetchone()
                        next_addr_id = (result[0] or 0) + 1
                        address_id = f"ADDR{next_addr_id:04d}"
                        
                        cursor.execute("""
                            INSERT INTO address (address_id, address, city, state)
                            VALUES (%s, %s, %s, %s)
                        """, [
                            address_id,
                            data.get('address', ''),
                            data.get('city', ''),
                            data.get('state', '')
                        ])
                    
                    # Insert new human doctor with proper formatting
                    logger.info("Inserting human doctor")
                    cursor.execute("""
                        INSERT INTO human_doctors 
                        (doctor_id, first_name, last_name, gender_id, email, password_hash, 
                         phone_number, specialization, years_experience, registration_number, 
                         age, passout_date, status, address_id, open_time_1, close_time_1)
                        VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING doctor_id
                    """, [
                        data['firstName'].strip().title(),  # Proper case
                        data['lastName'].strip().title(),   # Proper case
                        gender_id,
                        data['email'].strip().lower(),      # Lowercase email
                        password_hash,
                        data['phoneNumber'].strip(),
                        data['specialization'].strip().title(),  # Proper case
                        int(data['yearsExperience']),
                        data['registrationNumber'].strip().upper(),  # Uppercase reg number
                        int(data['age']), 
                        data['passoutDate'], 
                        'Active',  # Proper case
                        address_id,
                        '09:00:00',  # Default opening time
                        '17:00:00'   # Default closing time
                    ])
                    
                    doctor_id = cursor.fetchone()[0]
                    doctor_name = f"Dr. {data['firstName'].strip().title()} {data['lastName'].strip().title()}"
                    logger.info(f"Human doctor created: {doctor_id}")
                    
                else:  # vet
                    # Check if email already exists
                    cursor.execute("SELECT doctor_id FROM animal_doctors WHERE email = %s", [data['email']])
                    if cursor.fetchone():
                        return Response(
                            {'error': 'Email already registered'},
                            status=status.HTTP_409_CONFLICT
                        )
                    
                    # Generate vet doctor ID (max 10 chars)
                    logger.info("Generating vet doctor ID")
                    cursor.execute("""
                        SELECT COALESCE(MAX(CAST(SUBSTRING(doctor_id FROM 2) AS INTEGER)), 0) 
                        FROM animal_doctors 
                        WHERE doctor_id ~ '^V[0-9]+$'
                    """)
                    result = cursor.fetchone()
                    next_id = (result[0] or 0) + 1
                    vet_id = f"V{next_id:03d}"
                    logger.info(f"Generated vet ID: {vet_id}")
                    
                    # Insert new vet doctor with proper formatting
                    logger.info("Inserting vet doctor")
                    cursor.execute("""
                        INSERT INTO animal_doctors 
                        (doctor_id, name, email, password_hash, phone, specialty, 
                         experience, registration_number, age, passout_date, 
                         gender, clinic_name, address, city, state, license_number,
                         open_time_1, close_time_1)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [
                        vet_id,
                        f"Dr. {data['firstName'].strip().title()} {data['lastName'].strip().title()}", 
                        data['email'].strip().lower(), 
                        password_hash, 
                        data['phoneNumber'].strip(),
                        data['specialization'].strip().title(), 
                        int(data['yearsExperience']),
                        data['registrationNumber'].strip().upper(), 
                        int(data['age']), 
                        data['passoutDate'],
                        data['gender'][:10],
                        data.get('clinicName', '').strip().title()[:150],
                        data.get('address', '').strip(),
                        data.get('city', '').strip().title()[:100],
                        data.get('state', '').strip().title()[:100],
                        data['registrationNumber'].strip().upper()[:20],
                        '09:00:00',  # Default opening time
                        '17:00:00'   # Default closing time
                    ])
                    
                    doctor_id = vet_id
                    doctor_name = f"Dr. {data['firstName'].strip().title()} {data['lastName'].strip().title()}"
                    logger.info(f"Vet doctor created: {doctor_id}")
        
        return Response({
            'success': True,
            'message': 'Registration successful',
            'doctor_id': doctor_id,
            'doctor_name': doctor_name
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Registration error:\n{error_details}")
        print(f"=== REGISTRATION ERROR ===")
        print(error_details)
        print(f"=========================")
        return Response(
            {'error': f'Registration failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_doctor_appointments(request):
    """
    Get all appointments for a doctor
    Query params: doctor_id, type (human/vet)
    """
    doctor_id = request.query_params.get('doctor_id')
    doctor_type = request.query_params.get('type', 'human')
    filter_type = request.query_params.get('filter', None)  # 'upcoming' or 'past'

    if not doctor_id:
        return Response(
            {'error': 'doctor_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    from datetime import date
    today = date.today()

    def is_attended(status):
        if not status:
            return False
        return status.lower() in ['attended', 'completed', 'done']

    try:
        if doctor_type == 'human':
            qs = HumanAppointment.objects.filter(doctor_id=doctor_id).select_related('patient', 'doctor')
            if filter_type == 'upcoming':
                qs = qs.filter(
                    models.Q(scheduling_date__gt=today) |
                    (models.Q(scheduling_date=today) & ~models.Q(status__iexact='attended') & ~models.Q(status__iexact='completed') & ~models.Q(status__iexact='done'))
                )
            elif filter_type == 'past':
                qs = qs.filter(
                    models.Q(scheduling_date__lt=today) |
                    models.Q(status__iexact='attended') |
                    models.Q(status__iexact='completed') |
                    models.Q(status__iexact='done')
                )
            appointments = qs.order_by('-scheduling_date', '-scheduling_time')
            appointments_data = []
            for apt in appointments:
                appointments_data.append({
                    'appointment_id': apt.appointment_id,
                    'patient_first_name': apt.patient.first_name,
                    'patient_last_name': apt.patient.last_name,
                    'contact_number': apt.patient.contact_number,
                    'scheduling_date': apt.scheduling_date,
                    'scheduling_time': apt.scheduling_time,
                    'status': apt.status or 'scheduled',
                    'age': apt.age
                })
        else:
            qs = AnimalAppointment.objects.filter(doctor_id=doctor_id).select_related('animal', 'animal__owner', 'doctor')
            if filter_type == 'upcoming':
                qs = qs.filter(
                    models.Q(appointment_date__gt=today) |
                    (models.Q(appointment_date=today) & ~models.Q(status__iexact='attended') & ~models.Q(status__iexact='completed') & ~models.Q(status__iexact='done'))
                )
            elif filter_type == 'past':
                qs = qs.filter(
                    models.Q(appointment_date__lt=today) |
                    models.Q(status__iexact='attended') |
                    models.Q(status__iexact='completed') |
                    models.Q(status__iexact='done')
                )
            appointments = qs.order_by('-appointment_date')
            appointments_data = []
            for apt in appointments:
                appointments_data.append({
                    'appointment_id': apt.appointment_id,
                    'animal_name': apt.animal.animal_name,
                    'species': apt.animal.species,
                    'breed': apt.animal.breed,
                    'owner_name': apt.animal.owner.owner_name,
                    'owner_phone': apt.animal.owner.phone,
                    'appointment_date': apt.appointment_date,
                    'status': apt.status or 'scheduled'
                })

        return Response({
            'success': True,
            'appointments': appointments_data,
            'total': len(appointments_data)
        })

    except Exception as e:
        return Response(
            {'error': f'Failed to fetch appointments: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



@api_view(['GET'])
def get_doctor_profile(request):
    """
    Get doctor profile information
    Query params: doctor_id, type (human/vet)
    """
    doctor_id = request.query_params.get('doctor_id')
    doctor_type = request.query_params.get('type', 'human')
    
    if not doctor_id:
        return Response(
            {'error': 'doctor_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        from django.db import connection
        
        if doctor_type == 'human':
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT h.doctor_id, h.first_name, h.last_name, h.email, h.phone_number,
                           h.specialization, h.years_experience, h.registration_number,
                           h.status, h.open_time_1, h.close_time_1, h.open_time_2, h.close_time_2,
                           a.address, a.city, a.state
                    FROM human_doctors h
                    LEFT JOIN address a ON h.address_id = a.address_id
                    WHERE h.doctor_id = %s
                """, [doctor_id])
                
                row = cursor.fetchone()
                if not row:
                    return Response({'error': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)
                
                profile = {
                    'doctor_id': row[0],
                    'first_name': row[1],
                    'last_name': row[2],
                    'email': row[3],
                    'phone_number': row[4],
                    'specialization': row[5],
                    'years_experience': row[6],
                    'registration_number': row[7],
                    'status': row[8],
                    'open_time_1': str(row[9]) if row[9] else None,
                    'close_time_1': str(row[10]) if row[10] else None,
                    'open_time_2': str(row[11]) if row[11] else None,
                    'close_time_2': str(row[12]) if row[12] else None,
                    'address': row[13],
                    'city': row[14],
                    'state': row[15]
                }
        else:  # vet
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT doctor_id, name, email, phone, specialty, experience,
                           registration_number, open_time_1, close_time_1, 
                           open_time_2, close_time_2, address, city, state, clinic_name
                    FROM animal_doctors
                    WHERE doctor_id = %s
                """, [doctor_id])
                
                row = cursor.fetchone()
                if not row:
                    return Response({'error': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)
                
                profile = {
                    'doctor_id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'phone': row[3],
                    'specialty': row[4],
                    'experience': row[5],
                    'registration_number': row[6],
                    'open_time_1': str(row[7]) if row[7] else None,
                    'close_time_1': str(row[8]) if row[8] else None,
                    'open_time_2': str(row[9]) if row[9] else None,
                    'close_time_2': str(row[10]) if row[10] else None,
                    'address': row[11],
                    'city': row[12],
                    'state': row[13],
                    'clinic_name': row[14],
                    'status': 'Active'  # Default for vet doctors
                }
        
        return Response({
            'success': True,
            'profile': profile
        })
        
    except Exception as e:
        import traceback
        print(f"Get profile error: {traceback.format_exc()}")
        return Response(
            {'error': f'Failed to fetch profile: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
def update_doctor_profile(request):
    """
    Update doctor profile information
    Body: { doctor_id, type, address, city, state, openTime1, closeTime1, openTime2, closeTime2, status }
    """
    from django.db import connection, transaction
    
    doctor_id = request.data.get('doctor_id')
    doctor_type = request.data.get('type', 'human')
    
    if not doctor_id:
        return Response(
            {'error': 'doctor_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                if doctor_type == 'human':
                    # Update or create address
                    address_id = None
                    if request.data.get('address') or request.data.get('city') or request.data.get('state'):
                        # Get existing address_id
                        cursor.execute("SELECT address_id FROM human_doctors WHERE doctor_id = %s", [doctor_id])
                        result = cursor.fetchone()
                        if result and result[0]:
                            address_id = result[0]
                            # Update existing address
                            cursor.execute("""
                                UPDATE address 
                                SET address = %s, city = %s, state = %s
                                WHERE address_id = %s
                            """, [
                                request.data.get('address', ''),
                                request.data.get('city', ''),
                                request.data.get('state', ''),
                                address_id
                            ])
                        else:
                            # Create new address
                            cursor.execute("SELECT COALESCE(MAX(CAST(SUBSTRING(address_id FROM 5) AS INTEGER)), 0) FROM address WHERE address_id ~ '^ADDR[0-9]+'")
                            result = cursor.fetchone()
                            next_addr_id = (result[0] or 0) + 1
                            address_id = f"ADDR{next_addr_id:04d}"
                            
                            cursor.execute("""
                                INSERT INTO address (address_id, address, city, state)
                                VALUES (%s, %s, %s, %s)
                            """, [
                                address_id,
                                request.data.get('address', ''),
                                request.data.get('city', ''),
                                request.data.get('state', '')
                            ])
                    
                    # Update doctor profile
                    cursor.execute("""
                        UPDATE human_doctors
                        SET open_time_1 = %s, close_time_1 = %s,
                            open_time_2 = %s, close_time_2 = %s,
                            status = %s, address_id = %s
                        WHERE doctor_id = %s
                    """, [
                        request.data.get('openTime1') or None,
                        request.data.get('closeTime1') or None,
                        request.data.get('openTime2') or None,
                        request.data.get('closeTime2') or None,
                        request.data.get('status', 'Active'),
                        address_id,
                        doctor_id
                    ])
                    
                else:  # vet
                    cursor.execute("""
                        UPDATE animal_doctors
                        SET address = %s, city = %s, state = %s,
                            open_time_1 = %s, close_time_1 = %s,
                            open_time_2 = %s, close_time_2 = %s
                        WHERE doctor_id = %s
                    """, [
                        request.data.get('address', ''),
                        request.data.get('city', ''),
                        request.data.get('state', ''),
                        request.data.get('openTime1') or None,
                        request.data.get('closeTime1') or None,
                        request.data.get('openTime2') or None,
                        request.data.get('closeTime2') or None,
                        doctor_id
                    ])
        
        return Response({
            'success': True,
            'message': 'Profile updated successfully'
        })
        
    except Exception as e:
        import traceback
        print(f"Update profile error: {traceback.format_exc()}")
        return Response(
            {'error': f'Failed to update profile: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
