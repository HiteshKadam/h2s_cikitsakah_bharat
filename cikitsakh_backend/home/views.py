from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.db.models import Q
from math import radians, cos, sin, asin, sqrt
from .models import HumanDoctor, VetDoctor, Patient, Animal, Address
from .serializers import (
    HumanDoctorSerializer, VetDoctorSerializer,
    PatientSerializer, AnimalSerializer
)
from .ml.symptom_analyzer import SymptomAnalyzer


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
    
    analyzer = SymptomAnalyzer()
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
    """
    symptoms = request.data.get('symptoms', '')
    patient_type = request.data.get('patient_type', 'human')
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    initial_radius = request.data.get('radius', 10)
    
    if not symptoms:
        return Response({'error': 'Symptoms are required'}, status=status.HTTP_400_BAD_REQUEST)
    
    analyzer = SymptomAnalyzer()
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
    Create a new appointment for human patient
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
            'patient_created': created
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
    Create a new appointment for animal patient
    """
    from .serializers import CreateAnimalAppointmentSerializer
    from .models import Owner
    
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
            existing_appointments = HumanAppointment.objects.filter(
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
            
            existing_appointments = AnimalAppointment.objects.filter(
                doctor=doctor,
                appointment_date=appointment_date,
                status__in=['scheduled', 'confirmed']
            ).values_list('appointment_date', flat=True)
        
        # Generate time slots (30-minute intervals)
        slots = []
        current_time = datetime.combine(appointment_date, start_time)
        end_datetime = datetime.combine(appointment_date, end_time)
        
        while current_time < end_datetime:
            slot_time = current_time.time()
            is_available = slot_time not in existing_appointments
            
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
