# REPLACE the search_doctors_by_symptoms function in views.py with this code

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
